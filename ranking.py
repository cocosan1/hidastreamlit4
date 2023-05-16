import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl

from func_collection import Graph

st.set_page_config(page_title='ranking')
st.markdown('#### 品番別分析')

# ***ファイルアップロード***
uploaded_file = st.sidebar.file_uploader('Excel', type='xlsx', key='xlsx')
df = DataFrame()
if uploaded_file:
    df = pd.read_excel(
    uploaded_file, sheet_name='受注委託移動在庫生産照会', usecols=[2, 8, 9, 10, 15, 31, 42, 50, 51]) #index　ナンバー不要　index_col=0
else:
    st.info('今期のファイルを選択してください。')
    st.stop()
    
df['数量'] = df['数量'].fillna(0).astype('int64')
df['金額'] = df['金額'].fillna(0).astype('int64')
df['原価金額'] = df['原価金額'].fillna(0).astype('int64')

df['得意先CD2'] = df['得意先CD'].map(lambda x:str(x)[0:5])
df['商品コード2'] = df['商品コード'].map(lambda x: x.split()[0]) #品番


df['張地'] = df['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
df['HTSサイズ'] = df['張地'].map(lambda x: x.split('x')[0]) #HTSサイズ
df['HTS形状'] = df['商　品　名'].map(lambda x: x.split()[1] if len(x.split()) >= 4 else '') #HTS天板形状
df['HTS形状2'] = df['HTS形状'].map(lambda x: x.split('形')[0] if len(x.split('形')) >= 2 else '') #面型抜き


df2 = df[df['商品分類名2'].isin(['ダイニングチェア', 'リビングチェア'])]

#graphインスタンス
graph = Graph()

#*********************************************************************************関数
#***********************************bar
# def make_bar(val_list, x_list):
#     #可視化
#     #グラフを描くときの土台となるオブジェクト
#     fig = go.Figure()
#     #今期のグラフの追加
#     for (val, x) in zip(val_list, x_list):
#         fig.add_trace(
#             go.Bar(
#                 x=[x],
#                 y=[val],
#                 text=[round(val/10000) if int(val) >= 10000 else int(val)],
#                 textposition="outside", 
#                 name=x)
#         )
#     #レイアウト設定     
#     fig.update_layout(
#         showlegend=False #凡例表示
#     )
#     #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
#     st.plotly_chart(fig, use_container_width=True) 

def ranking_series():
    # *** selectbox 商品分類2***
    category = ['リビングチェア', 'ダイニングチェア']
    option_category = st.selectbox(
        'category:',
        category,   
    )
    df_cate = df2[df2['商品分類名2']==option_category]

    # *** selectbox シリーズ名***
    series_list = df_cate['シリーズ名'].unique()
    option_series = st.selectbox(
        'series:',
        series_list,   
    )
    df_cate_seri = df_cate[df_cate['シリーズ名']==option_series]
        
    df_cate_seri = df_cate_seri[df_cate_seri['張地'] != ''] #空欄を抜いたdf作成

    df_result= df_cate_seri.groupby(['張地'])['数量'].sum().sort_values(ascending=False).head(12)

    st.markdown('##### ランキング 張地別')
    
    graph.make_bar(df_result, df_result.index)

def ranking_item():
    # *** selectbox 商品分類2***
    category = ['ダイニングチェア', 'リビングチェア']
    option_category = st.selectbox(
        'category:',
        category,   
    )
    df_cate = df2[df2['商品分類名2']==option_category]

    with st.form('入力フォーム'):
        # *** selectbox シリーズ名***
        series_list = df_cate['シリーズ名'].unique()
        option_series = st.selectbox(
            'series:',
            series_list,   
        )
        df_cate_seri = df_cate[df_cate['シリーズ名']==option_series]

        # *** selectbox 塗色***
        color_list = df_cate_seri['塗色CD'].unique()
        option_color = st.selectbox(
            'color:',
            color_list,   
        )
        st.form_submit_button('submit')
        
    df_cate_seri_col = df_cate_seri[df_cate_seri['塗色CD']==option_color]
    df_cate_seri_col = df_cate_seri_col[df_cate_seri_col['張地'] != ''] #空欄を抜いたdf作成

    df_result= df_cate_seri_col.groupby(['張地'])['数量'].sum().sort_values(ascending=False).head(12)

    #脚カットの場合ファブリックの位置がずれる為、行削除
    for index in df_result.index:
        if index in ['ｾﾐｱｰﾑﾁｪｱ', 'ｱｰﾑﾁｪｱ', 'ﾁｪｱ']:
            df_result.drop(index=index, inplace=True)

    # グラフ　張布売り上げ
    st.write('ランキング 張地別')

    graph.make_bar(df_result, df_result.index)


def profit():
    hinban = st.text_input('品番を入力', 'SG261A')
    col1, col2 = st.columns(2)
    with col1:
        kingaku_sum = df[df['商品コード2']==hinban]['金額'].sum()
        genka_sum = df[df['商品コード2']==hinban]['原価金額'].sum()
        st.metric('粗利率', value=(f'{(kingaku_sum-genka_sum)/kingaku_sum*100:0.1f} %'))
    
    with col2:
        profit = kingaku_sum-genka_sum
        st.metric('粗利額', value='{:,}'.format(profit))


def hts_width():
    df_hts = df[df['商品コード2']=='HTS2']
    size_list = df_hts['HTSサイズ'].unique() #張地だがサイズを拾える

    #strに型変換してグラフ作成時に順番が動かないようにする
    str_list = []
    for size in size_list:
        str_list.append(str(size))

    cnt_list = []
    windex = []

    #ランキング用indexにW追加
    wstr_list = ['W'+ str_name for str_name in str_list]

    for (size, wstr_size) in zip(size_list, wstr_list):
        windex.append(wstr_size)
        cnt = df_hts[df_hts['HTSサイズ']==size]['数量'].sum()
        cnt_list.append(cnt)

    #オリジナル
    s_wsize = pd.Series(cnt_list, index=windex)
    s_wsize = s_wsize.head(12)

    #ランキング用
    s_wsize2 = s_wsize.sort_values(ascending=False)

    #分布用

    s_wsize3 = s_wsize.sort_index(ascending=True)

    st.markdown('##### 侭サイズ別数量/ランキング')
   
    graph.make_bar(s_wsize2, s_wsize2.index)

    st.markdown('##### 侭サイズ別数量/分布')

    graph.make_bar(s_wsize3, s_wsize3.index)


def hts_shape():
    df_hts = df[df['商品コード2']=='HTS2']
    shape_list = df_hts['HTS形状'].unique()

    cnt_list = []
    index = []

    for shape in shape_list:
        index.append(shape)
        cnt = df_hts[df_hts['HTS形状']==shape]['数量'].sum()
        cnt_list.append(cnt)

    df_shape = pd.DataFrame(index=index)
    df_shape['数量'] = cnt_list
    df_shape = df_shape.sort_values(by='数量', ascending=False)
    df_shape2 = df_shape.head(12)

    st.markdown('###### 天板/面形状ランキング')
  
    graph.make_bar(df_shape2['数量'], df_shape2.index)

def hts_shapesize():
    df_hts = df[df['商品コード2']=='HTS2']
    df_hts['形状サイズ'] = df_hts['HTS形状'] + df_hts['HTSサイズ']
    shapesize_list = df_hts['形状サイズ'].unique()

    cnt_list = []
    index_list = []

    for shapesize in shapesize_list:
        index_list.append(shapesize)
        cnt = df_hts[df_hts['形状サイズ']==shapesize]['数量'].sum()
        cnt_list.append(cnt)

    df_shapesize = pd.DataFrame(index=index_list)
    df_shapesize['数量'] = cnt_list
    df_shapesize = df_shapesize.sort_values(by='数量', ascending=False)
    df_shapesize2 = df_shapesize.head(12)

    st.markdown('###### 天板/面形状＆サイズランキング')
  
    graph.make_bar(df_shapesize2['数量'], df_shapesize2.index)


def hts_shapesize_nonedge():
    df_hts = df[df['商品コード2']=='HTS2']
    df_hts['形状2サイズ'] = df_hts['HTS形状2'] + df_hts['HTSサイズ']
    shapesize_list = df_hts['形状2サイズ'].unique()

    cnt_list = []
    index_list = []

    for shapesize in shapesize_list:
        index_list.append(shapesize)
        cnt = df_hts[df_hts['形状2サイズ']==shapesize]['数量'].sum()
        cnt_list.append(cnt)

    df_shapesize = pd.DataFrame(index=index_list)
    df_shapesize['数量'] = cnt_list
    df_shapesize = df_shapesize.sort_values(by='数量', ascending=False)
    df_shapesize2 = df_shapesize.head(12)

    st.markdown('###### 天板形状＆サイズ　一覧 ※面形状抜き')
    
    graph.make_bar(df_shapesize2['数量'], df_shapesize2.index)

def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '張地ランキング/シリーズ': ranking_series,
        '張地ランキング/シリーズ/塗色': ranking_item,
        '品番別粗利率/粗利額': profit,
        '侭　サイズランキング': hts_width,
        '侭　天板面形状ランキング': hts_shape,
        '侭　天板面形状サイズランキング': hts_shapesize,
        '侭　天板形状サイズランキング': hts_shapesize_nonedge
          
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))
    link = '[home](https://cocosan1-hidastreamlit4-linkpage-7tmz81.streamlit.app/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る')                                       

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

if __name__ == '__main__':
    main()
