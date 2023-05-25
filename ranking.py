import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
import datetime

from sklearn.preprocessing import StandardScaler

from func_collection import Graph

st.set_page_config(page_title='ranking')
st.markdown('#### 品番別分析')

@st.cache_data(ttl=datetime.timedelta(hours=1))
def make_data_now(file):
    df_now = pd.read_excel(
    file, sheet_name='受注委託移動在庫生産照会', \
        usecols=[2, 8, 9, 10, 15, 16, 31, 42, 50, 51]) #index　ナンバー不要　index_col=0

    df_now['得意先CD2'] = df_now['得意先CD'].map(lambda x:str(x)[0:5])
    df_now['商品コード2'] = df_now['商品コード'].map(lambda x: x.split()[0]) #品番


    df_now['張地'] = df_now['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
    df_now['HTSサイズ'] = df_now['張地'].map(lambda x: x.split('x')[0]) #HTSサイズ
    df_now['HTS形状'] = df_now['商　品　名'].map(lambda x: x.split()[1] if len(x.split()) >= 4 else '') #HTS天板形状
    df_now['HTS形状2'] = df_now['HTS形状'].map(lambda x: x.split('形')[0] if len(x.split('形')) >= 2 else '') #面型抜き

    # ***INT型への変更***
    df_now[['数量', '金額', '原価金額']] = df_now[['数量', '金額', '原価金額']].fillna(0).astype('int64')
    #fillna　０で空欄を埋める


    return df_now

@st.cache_data(ttl=datetime.timedelta(hours=1))
def make_data_last(file):
    df_last = pd.read_excel(
    file, sheet_name='受注委託移動在庫生産照会', \
        usecols=[2, 8, 9, 10, 15, 16, 31, 42, 50, 51])
    
    df_last['得意先CD2'] = df_last['得意先CD'].map(lambda x:str(x)[0:5])
    df_last['商品コード2'] = df_last['商品コード'].map(lambda x: x.split()[0]) #品番

    df_last['張地'] = df_last['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')
    df_last['HTSサイズ'] = df_last['張地'].map(lambda x: x.split('x')[0]) #HTSサイズ
    df_last['HTS形状'] = df_last['商　品　名'].map(lambda x: x.split()[1] if len(x.split()) >= 4 else '') #HTS天板形状
    df_last['HTS形状2'] = df_last['HTS形状'].map(lambda x: x.split('形')[0] if len(x.split('形')) >= 2 else '') #面型抜き

    # ***INT型への変更***
    df_last[['数量', '金額', '原価金額']] = df_last[['数量', '金額', '原価金額']].fillna(0).astype('int64')
    #fillna　０で空欄を埋める

    return df_last        


# ***ファイルアップロード 今期***
uploaded_file_now = st.sidebar.file_uploader('今期', type='xlsx', key='now')
df_now = DataFrame()
if uploaded_file_now:
    df_now = make_data_now(uploaded_file_now)

    #データ範囲表示
    date_start =df_now['受注日'].min()
    date_end =df_now['受注日'].max()
    st.sidebar.caption(f'{date_start} - {date_end}')

else:
    st.info('今期のファイルを選択してください。')


# ***ファイルアップロード　前期***
uploaded_file_last = st.sidebar.file_uploader('前期', type='xlsx', key='last')
df_last = DataFrame()
if uploaded_file_last:
    df_last = make_data_last(uploaded_file_last)

    #データ範囲表示
    date_start =df_last['受注日'].min()
    date_end =df_last['受注日'].max()
    st.sidebar.caption(f'{date_start} - {date_end}')
    
else:
    st.info('前期のファイルを選択してください。')
    st.stop()


df2 = df_now[df_now['商品分類名2'].isin(['ダイニングチェア', 'リビングチェア'])]

#graphインスタンス
graph = Graph()

def calc_deviation():
    st.markdown('### アイテム上昇・下降分析/偏差値')
    cate_list = ['リビングチェア', 'ダイニングチェア', 'ダイニングテーブル']
    selected_cate = st.selectbox(
        '商品分類',
        cate_list,
        key='cl'
    )
    df_now2 = df_now[df_now['商品分類名2']==selected_cate]
    df_last2 = df_last[df_last['商品分類名2']==selected_cate]

    df_now2['品番'] = df_now2['商　品　名'].apply(lambda x: x.split(' ')[0])
    df_last2['品番'] = df_last2['商　品　名'].apply(lambda x: x.split(' ')[0])

    df_now2['数量'] = df_now2['数量'].fillna(0)
    df_last2['数量'] = df_last2['数量'].fillna(0)


    s_now2g = df_now2.groupby('品番')['数量'].sum()
    s_last2g = df_last2.groupby('品番')['数量'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.write('今期')
        st.write(s_now2g)

        #外れ値処理
        st.write('外れ値処理')
        under_now = st.number_input('下限指定', key='unn', value=0)
        upper_now = st.number_input('上限指定', key='upn', value=100)

        s_now2g = s_now2g[(s_now2g >= under_now) & (s_now2g <= upper_now)]
        with st.expander('外れ値処理後', expanded=False):
            st.write(s_now2g)

    with col2:
        st.write('前期')
        st.write(s_last2g)  

        #外れ値処理
        st.write('外れ値処理')
        under_last = st.number_input('下限指定', key='unl', value=0)
        upper_last = st.number_input('上限指定', key='upl', value=100)

        s_last2g = s_last2g[(s_last2g >= under_last) & (s_last2g <= upper_last)]
        with st.expander('外れ値処理後', expanded=False):
            st.write(s_last2g)


    #標準化
    #今期
    scaler = StandardScaler()
    s_now2gr = s_now2g.values.reshape(-1, 1) #.values忘れない #reshape(-1, 1)で縦配列に
    sd_now = scaler.fit_transform(s_now2gr)
    df_sdnow = pd.DataFrame(sd_now, columns=['今期'], index=s_now2g.index)

    #前期
    s_last2gr = s_last2g.values.reshape(-1, 1) #.values忘れない #reshape(-1, 1)で縦配列に
    sd_last = scaler.fit_transform(s_last2gr)
    df_sdlast = pd.DataFrame(sd_last, columns=['前期'], index=s_last2g.index)

    #merge
    df_m = df_sdnow.merge(df_sdlast, left_index=True, right_index=True, how='left')
    df_m = df_m.fillna(0)

    df_m['dev今期'] = df_m['今期'].apply(lambda x: (x*10)+50)
    df_m['dev前期'] = df_m['前期'].apply(lambda x: (x*10)+50)

    df_m['差異'] = df_m['dev今期'] - df_m['dev前期']
    df_m['比率'] = df_m['dev今期'] / df_m['dev前期']

    #偏差値
    item_list = ['上昇アイテム', '下降アイテム']
    selected_item = st.selectbox(
        'アイテム選択',
        item_list,
        key='il'
    )

    #数量が平均より少ないアイテムの削除

    df_now2g2 = pd.DataFrame(s_now2g)
    df_last2g2 = pd.DataFrame(s_last2g)
    df_mval = df_now2g2.merge(df_last2g2, left_index=True, right_index=True, how='left')


    if selected_item == '上昇アイテム':
        df_up = df_m.sort_values(['比率', 'dev今期'], ascending=False)
        df_upm = df_up.merge(df_mval, left_index=True, right_index=True, how='left')
        df_upm.drop(['今期', '前期'], axis=1, inplace=True)
        df_upm = df_upm.rename(columns={'数量_x': '今期/数量', '数量_y': '前期/数量'})
        df_upm = df_upm[df_upm['比率'] >= 1]


        st.dataframe(df_upm)
    
    elif selected_item == '下降アイテム':
        df_down = df_m.sort_values('dev今期', ascending=False)
        df_down = df_m.sort_values('比率', ascending=True)
        df_downm = df_down.merge(df_mval, left_index=True, right_index=True, how='left')
        df_downm.drop(['今期', '前期'], axis=1, inplace=True)
        df_downm = df_downm.rename(columns={'数量_x': '今期/数量', '数量_y': '前期/数量'})
        df_downm = df_downm[df_downm['比率'] <= 1]

        st.dataframe(df_downm)

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
        kingaku_sum = df_now[df_now['商品コード2']==hinban]['金額'].sum()
        genka_sum = df_now[df_now['商品コード2']==hinban]['原価金額'].sum()
        st.metric('粗利率', value=(f'{(kingaku_sum-genka_sum)/kingaku_sum*100:0.1f} %'))
    
    with col2:
        profit = kingaku_sum-genka_sum
        st.metric('粗利額', value='{:,}'.format(profit))


def hts_width():
    df_hts = df_now[df_now['商品コード2']=='HTS2']
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
    df_hts = df_now[df_now['商品コード2']=='HTS2']
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
    df_hts = df_now[df_now['商品コード2']=='HTS2']
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
    df_hts = df_now[df_now['商品コード2']=='HTS2']
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
        '侭　天板形状サイズランキング': hts_shapesize_nonedge,
        'test':calc_deviation
          
    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))                                     

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()

    link = '[home](https://cocosan1-hidastreamlit4-linkpage-7tmz81.streamlit.app/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る') 

if __name__ == '__main__':
    main()
