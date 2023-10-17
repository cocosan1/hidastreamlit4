import pandas as pd
# import numpy as np
from pandas.core.frame import DataFrame
import streamlit as st
# import plotly.figure_factory as ff
import plotly.graph_objects as go
import openpyxl
import datetime

from func_collection import Graph

st.set_page_config(page_title='売り上げ分析')
st.markdown('## 売り上げ分析')

@st.cache_data(ttl=datetime.timedelta(hours=1))
def make_data_now(file):
    df_now = pd.read_excel(
    file, sheet_name='受注委託移動在庫生産照会', \
        usecols=[1, 3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52]) #index　ナンバー不要　index_col=0

    # *** 出荷月、受注月列の追加***
    df_now['出荷月'] = df_now['出荷日'].dt.month
    # df_now['受注年月'] = df_now['受注日'].dt.strftime("%Y-%m")
    # df_now['受注年月'] = pd.to_datetime(df_now['受注年月'])
    df_now['商品コード2'] = df_now['商　品　名'].map(lambda x: x.split()[0]) #品番
    df_now['商品コード3'] = df_now['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
    df_now['張地'] = df_now['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '') 

    # ***INT型への変更***
    df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月']] = \
        df_now[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月']].fillna(0).astype('int64')
    #fillna　０で空欄を埋める

    return df_now

@st.cache_data(ttl=datetime.timedelta(hours=1))
def make_data_last(file):
    df_last = pd.read_excel(
    uploaded_file_last, sheet_name='受注委託移動在庫生産照会', \
        usecols=[1, 3, 6, 8, 10, 14, 15, 16, 28, 31, 42, 50, 51, 52])
    df_last['出荷月'] = df_last['出荷日'].dt.month
    df_last['受注年月'] = df_last['受注日'].dt.strftime("%Y-%m")
    df_last['受注年月'] = pd.to_datetime(df_last['受注年月'])
    df_last['商品コード2'] = df_last['商　品　名'].map(lambda x: x.split()[0])
    df_last['商品コード3'] = df_last['商　品　名'].map(lambda x: str(x)[0:2]) #頭品番
    df_last['張地'] = df_last['商　品　名'].map(lambda x: x.split()[2] if len(x.split()) >= 4 else '')

    df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月']] = \
        df_last[['数量', '単価', '金額', '出荷倉庫', '原価金額', '出荷月']].fillna(0).astype('int64')
    #fillna　０で空欄を埋める

    return df_last         

with st.sidebar.expander('説明/タブ', expanded=False):
    st.write('全体')
    st.caption('全体の分析')
    st.write('得意先一覧')
    st.caption('得意先別に一覧で分析')
    st.write('得意先個別')
    st.caption('得意先を個別で分析')
    st.write('エリア')
    st.caption('地域単位で分析')
    st.write('TIF')
    st.caption('ＴＩＦオリジナル中心に分析')
    st.caption('※ＴＩＦのみのデータを使用')


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



#グラフ生成クラス
graph = Graph()
    
#************************累計売上
now_total = df_now['金額'].sum()
last_total = df_last['金額'].sum()

tab1, tab2, tab3, tab4, tab5 = st.tabs(['全体', '得意先一覧', '得意先個別', 'エリア', 'TIF'])

#**********************************************************************************************tab1
with tab1:
    st.markdown('### ■ 全体')
    def none():
        st.info('分析項目を選択してしてください')
    #********************************************************************売上累計/前年比
    def earnings_comparison_year():
        
        
        total_comparison = f'{now_total / last_total * 100: 0.1f} %'
        total_diff = '{:,}'.format(now_total - last_total)

        col1, col2 = st.columns(2)
        with col1:
            st.metric('対前年比', value= total_comparison)
        with col2:
            st.metric('対前年差', value= total_diff)

        st.markdown('##### 売上（累計）')
        val_list = [now_total, last_total]
        x_list = ['今期', '前期']

        graph_ecy = Graph()
        graph_ecy.make_bar(val_list, x_list)    

    #*********************************************************************月別売上/前年比
    def earnings_comparison_month():

        #年月表記
        df_now2 = df_now.sort_values('受注日')
        df_now2['受注年月'] = df_now2['受注日'].dt.strftime("%Y-%m")

        df_last2 = df_last.sort_values('受注日')
        df_last2['受注年月'] = df_last2['受注日'].dt.strftime("%Y-%m")

        #index用monthリスト
        month_list = df_now2['受注年月'].unique()


        sales_now = []
        sales_last = []
        df_month = pd.DataFrame(index=month_list)

        for (month_now, month_last) in zip(df_now2['受注年月'].unique(), df_last2['受注年月'].unique()):
            sales_now_month =df_now2[df_now2['受注年月']==month_now]['金額'].sum()
            sales_last_month =df_last2[df_last2['受注年月']==month_last]['金額'].sum()

            sales_now.append(sales_now_month)
            sales_last.append(sales_last_month)

        df_month['今期売上'] = sales_now
        df_month['前期売上'] = sales_last

        df_month['対前期比'] = df_month['今期売上'] / df_month['前期売上']
        df_month['対前期差'] = df_month['今期売上'] - df_month['前期売上']
        df_month['累計(前期売上)'] = df_month['前期売上'].cumsum()
        df_month['累計(今期売上)'] = df_month['今期売上'].cumsum()
        df_month['累計(対前期比)'] = df_month['累計(今期売上)'] / df_month['累計(前期売上)']
        df_month['累計(対前期差)'] = df_month['累計(今期売上)'] - df_month['累計(前期売上)']

        df_month['対前期比'] = df_month['対前期比'].map('{:.1%}'.format)
        df_month['累計(対前期比)'] = df_month['累計(対前期比)'].map('{:.1%}'.format)

        df_month['今期売上'] = df_month['今期売上'].astype(int).apply('{:,}'.format)
        df_month['前期売上'] = df_month['前期売上'].astype(int).apply('{:,}'.format)
        df_month['対前期差'] = df_month['対前期差'].astype(int).apply('{:,}'.format)
        df_month['累計(前期売上)'] = df_month['累計(前期売上)'].astype(int).apply('{:,}'.format)
        df_month['累計(今期売上)'] = df_month['累計(今期売上)'].astype(int).apply('{:,}'.format)
        df_month['累計(対前期差)'] = df_month['累計(対前期差)'].astype(int).apply('{:,}'.format)

        #グラフ用にintデータ用意
        df_konki = df_month['今期売上'].apply(lambda x: x.replace(',', '')).astype(int)
        df_zenki = df_month['前期売上'].apply(lambda x: x.replace(',', '')).astype(int)
        df_rkonki = df_month['累計(今期売上)'].apply(lambda x: x.replace(',', '')).astype(int)
        df_rzenki = df_month['累計(前期売上)'].apply(lambda x: x.replace(',', '')).astype(int)

        with st.expander('詳細', expanded=False):
            st.markdown('###### 月別売上')
            st.table(df_month)

        #***************可視化
        #月別
        st.markdown('##### 月別売上')

        df_list = [df_konki, df_zenki]
        name_list =['今期', '前期']

        graph_ecm1 = Graph()
        graph_ecm1.make_line(df_list, name_list, month_list)


        #累計
        st.markdown('##### 月別累計売上')
        df_list = [df_rkonki, df_rzenki]
        name_list =['今期', '前期']

        graph.make_line(df_list, name_list, month_list)

    #*******************************************************************LD比率
    def living_dining_latio():

        living_now = df_now[df_now['商品分類名2'].isin(\
            ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = df_last[df_last['商品分類名2'].isin(\
            ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_diff = f'{(living_now/now_total*100) - (living_last/last_total*100): 0.1f} %'

        dining_now = df_now[df_now['商品分類名2'].isin(\
            ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = df_last[df_last['商品分類名2'].isin(\
            ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_diff = f'{(dining_now/now_total*100) - (dining_last/last_total*100): 0.1f} %'

        sonota_now = df_now[df_now['商品分類名2'].isin(\
            ['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
            'デスク', '小物・その他'])]['金額'].sum()
        sonota_last = df_last[df_last['商品分類名2'].isin(\
            ['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子',
            'デスク', '小物・その他'])]['金額'].sum()
        sonota_diff = f'{(sonota_now/now_total*100) - (sonota_last/last_total*100): 0.1f} %'

        #****************可視化
        #前年比
        st.markdown('##### LD別売上')
        list_now = [living_now, dining_now, sonota_now]
        list_last = [living_last, dining_last, sonota_last]
        x_list = ['リビング', 'ダイニング', 'その他']

        
        graph.make_bar_nowlast(list_now, list_last, x_list)

        st.markdown('##### LD比率')
        #比率
        fig_now = go.Figure()
        #***今期***
        fig_now.add_trace(
        go.Bar(
            name='リビング',  # データの名称（凡例に表示）
            x=['今期'],  # 横軸の値のリスト
            y=[living_now/now_total],  # 縦軸の値のリスト
            text=[f'リビング {living_now/now_total: 0.2f}' ],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(205, 92, 92, 1)'
        ))
        fig_now.add_trace(
        go.Bar(
            name='ダイニング',  # データの名称（凡例に表示）
            x=['今期'],  # 横軸の値のリスト
            y=[dining_now/now_total],  # 縦軸の値のリスト
            text=[f'ダイニング {dining_now/now_total: 0.2f}' ],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(240, 128, 128, 1)'
        ))
        fig_now.add_trace(
        go.Bar(
            name='その他',  # データの名称（凡例に表示）
            x=['今期'],  # 横軸の値のリスト
            y=[sonota_now/now_total],  # 縦軸の値のリスト
            text=[f'その他 {sonota_now/now_total: 0.2f}'],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(255, 160, 122, 1)'
        ))

        #***前期***
        fig_now.add_trace(
        go.Bar(
            name='リビング',  # データの名称（凡例に表示）
            x=['前期'],  # 横軸の値のリスト
            y=[living_last/last_total],  # 縦軸の値のリスト
            text=[f'{living_last/last_total: 0.2f}' ],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(205, 92, 92, 1)'
        ))
        fig_now.add_trace(
        go.Bar(
            name='ダイニング',  # データの名称（凡例に表示）
            x=['前期'],  # 横軸の値のリスト
            y=[dining_last/last_total],  # 縦軸の値のリスト
            text=[f'{dining_last/last_total: 0.2f}' ],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(240, 128, 128, 1)'
        ))
        fig_now.add_trace(
        go.Bar(
            name='その他',  # データの名称（凡例に表示）
            x=['前期'],  # 横軸の値のリスト
            y=[sonota_last/last_total],  # 縦軸の値のリスト
            text=[f'{sonota_last/last_total: 0.2f}'],  # 棒に記載するテキスト
            textposition="inside",
            marker_color='rgba(255, 160, 122, 1)'
        ))

        # グラフのレイアウトを変更
        fig_now.update_layout(
            showlegend=False, #凡例表示
            barmode="stack",

        )

        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig_now, use_container_width=True) 

        with st.expander('詳細', expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('リビング', value= '{:,}'.format(living_now), delta=int(living_now - living_last))
                #numpy intをintに変換
                st.caption(f'前年 {living_last}')
            with col2:
                st.metric('ダイニング', value= '{:,}'.format(dining_now), delta=int(dining_now - dining_last))
                #numpy intをintに変換
                st.caption(f'前年 {dining_last}') 
            with col3:
                st.metric('その他', value= '{:,}'.format(sonota_now), delta=int(sonota_now - sonota_last))
                #numpy intをintに変換
                st.caption(f'前年 {sonota_last}')        
            

        with st.expander('分類内訳', expanded=False):
            st.caption('リビング: クッション/リビングチェア/リビングテーブル')
            st.caption('ダイニング: ダイニングテーブル/ダイニングチェア/ベンチ')
            st.caption('その他: キャビネット類/その他テーブル/雑品・特注品/その他椅子/デスク/小物・その他')

    def living_dining_comparison_ld():

        # *** selectbox LD***
        category = ['リビング', 'ダイニング']
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        if option_category == 'リビング':
            df_now_cate = df_now[df_now['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
            df_last_cate = df_last[df_last['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        elif option_category == 'ダイニング':
            df_now_cate = df_now[df_now['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
            df_last_cate = df_last[df_last['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]

        index = []
        now_result = []
        last_result = []
        diff = []
        ratio = []
        series_list = df_now_cate['シリーズ名'].unique()
        
        for series in series_list:
            index.append(series)
            now_culc = df_now_cate[df_now_cate['シリーズ名']==series]['金額'].sum()
            last_culc = df_last_cate[df_last_cate['シリーズ名']==series]['金額'].sum()
            now_result.append(now_culc)
            last_result.append(last_culc)
            diff_culc = '{:,}'.format(now_culc - last_culc)
            diff.append(diff_culc)
            ratio_culc = f'{now_culc/last_culc*100:0.1f} %'
            ratio.append(ratio_culc)
        df_result = pd.DataFrame(list(zip(now_result, last_result, ratio, diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
        with st.expander('詳細', expanded=False):
            st.table(df_result)
        

        # グラフ
        #bar
        #前年比
        st.markdown('##### LD別シリーズ別売上')
        df_result = df_result.sort_values('今期', ascending=False)[:12] #今期売上順にソート
        graph.make_bar_nowlast(df_result['今期'], df_result['前期'], df_result.index)

        st.write(f'{option_category} 構成比(今期)')
        graph.make_pie(df_result['今期'], df_result.index)

        st.write(f'{option_category} 構成比(前期)')
        graph.make_pie(df_result['前期'], df_result.index)

    def hokkaido_fushi_kokusanzai():
        # *** 北海道比率　節材比率　国産材比率 ***
        col1, col2, col3 = st.columns(3)

        #分類の詳細
        with st.expander('分類の詳細'):
            st.write('【節あり】森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
            st.write('【国産材1】北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた\
                Kinoe/SUWARI/KURINOKI')
            st.write('【国産材2】SG261M/SG261K/SG261C/SG261AM/SG261AK/SG261AC/KD201M/KD201K/KD201C\
                    KD201AM/KD201AK/KD201AC')
        
        with col1:
            hokkaido_now = df_now[df_now['出荷倉庫']==510]['金額'].sum()
            hokkaido_last = df_last[df_last['出荷倉庫']==510]['金額'].sum()
            hokkaido_diff = f'{(hokkaido_now/now_total*100) - (hokkaido_last/last_total*100): 0.1f} %'
            st.metric('北海道工場比率', value=f'{hokkaido_now/now_total*100: 0.1f} %', delta=hokkaido_diff) #小数点以下1ケタ
            st.caption(f'前年 {hokkaido_last/last_total*100: 0.1f} %')
        with col2:
            fushi_now = df_now[df_now['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
            '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
            # sdソファ拾えていない isin その値を含む行　true
            fushi_last = df_last[df_last['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
            '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
            fushi_diff = f'{(fushi_now/now_total*100) - (fushi_last/last_total*100): 0.1f} %'
            st.metric('節材比率', value=f'{fushi_now/now_total*100: 0.1f} %', delta=fushi_diff) #小数点以下1ケタ
            st.caption(f'前年 {fushi_last/last_total*100: 0.1f} %')

        with col3:
            kokusanzai_now1 = df_now[df_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
            '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない
            kokusanzai_last1 = df_last[df_last['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
            '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない

            kokusanzai_now2 = df_now[df_now['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
            kokusanzai_last2 = df_last[df_last['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
            
            

            kokusanzai_now3 = df_now[df_now['商品コード3']=='HJ']['金額'].sum()
            kokusanzai_last3 = df_last[df_last['商品コード3']=='HJ']['金額'].sum()

            kokusanzai_now_t = kokusanzai_now1 + kokusanzai_now2 + kokusanzai_now3
            kokusanzai_last_t = kokusanzai_last1 + kokusanzai_last2 + kokusanzai_last3 

            with st.expander('国産材: 今期', expanded=False):
                df_now1 = df_now[df_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]
                df_now2 =df_now[df_now['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]
                df_now3 =df_now[df_now['商品コード3']=='HJ']

                st.table(df_now1[['得意先名', '商品コード2', '金額']])

            kokusanzai_diff = f'{(kokusanzai_now_t/now_total*100) - (kokusanzai_last_t/last_total*100): 0.1f} %'
            st.metric('国産材比率', value=f'{kokusanzai_now_t/now_total*100: 0.1f} %', delta=kokusanzai_diff) #小数点以下1ケタ
            st.caption(f'前年 {kokusanzai_last_t/last_total*100: 0.1f} %')

    def profit_aroma():
        col1, col2, col3 = st.columns(3)
        with col1:
            cost_now = df_now['原価金額'].sum()
            cost_last = df_last['原価金額'].sum()
            profitrate_diff = f'{((now_total-cost_now)/now_total*100) - ((last_total-cost_last)/last_total*100): 0.1f} %'
            st.metric('粗利率', value=f'{(now_total-cost_now)/now_total*100: 0.1f} %', delta=profitrate_diff)
            st.caption(f'前年 {(last_total-cost_last)/last_total*100: 0.1f} %')

        with col2:
            profit_diff = '{:,}'.format((now_total-cost_now) - (last_total-cost_last))
            st.metric('粗利額', value='{:,}'.format(now_total-cost_now), delta=profit_diff)
            profit_last = '{:,}'.format(last_total-cost_last)
            st.caption(f'前年 {profit_last} ')

        with col3:
            aroma_now = df_now[df_now['シリーズ名'].isin(['Essenntial Oil & Aroma Goods'])]['金額'].sum()
            aroma_last = df_last[df_last['シリーズ名'].isin(['Essenntial Oil & Aroma Goods'])]['金額'].sum()
            aroma_last2 = '{:,}'.format(aroma_last)
            aroma_diff = '{:,}'.format(aroma_now - aroma_last)
            st.metric('Essenntial Oil & Aroma Goods', value=('{:,}'.format(aroma_now)), delta=aroma_diff)
            st.caption(f'前年 {aroma_last2}')

    def color():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        st.caption('下段 構成比')
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]

        # ***塗色別売り上げ ***
        color_now = categorybase_now.groupby('塗色CD')['金額'].sum().sort_values(ascending=False)
        color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        # ***塗色別売り上げ ***
        color_last = categorybase_last.groupby('塗色CD')['金額'].sum().sort_values(ascending=False)
        color_last2 = color_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        #nowとlastの統合
        color_now.rename('今期', inplace=True)
        color_last.rename('前期', inplace=True)
        df_color = pd.concat([color_now, color_last], axis=1, join='outer')
        df_color = df_color.fillna(0)
        df_color = df_color.sort_values('今期', ascending=False)[:10]

        graph.make_bar_nowlast(df_color['今期'], df_color['前期'], df_color.index)

        col1, col2 = st.columns(2)
        with col1:
            # グラフ　シリーズ別売り上げ
            st.write('シリーズ別塗色別売上(今期)')
            graph.make_pie(df_color['今期'], df_color.index)

        with col2:
            # グラフ　シリーズ別売り上げ
            st.write('シリーズ別塗色別売上(前期)')
            graph.make_pie(df_color['前期'], df_color.index)

            
    def fabric():
        # *** selectbox ***
        category = ['ダイニングチェア', 'リビングチェア']
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        st.caption('下段 構成比')
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]
        
        # categorybase_now = categorybase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除
        # categorybase_last = categorybase_last.dropna(subset=['張地'])

        categorybase_now = categorybase_now[categorybase_now['張地'] != ''] #空欄を抜いたdf作成
        categorybase_last = categorybase_last[categorybase_last['張地'] != '']

        # ***張地別売り上げ ***
        fabric_now = categorybase_now.groupby('張地')['金額'].sum().sort_values(ascending=False)
        fabric_now2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        
        # ***張地別売り上げ ***
        fabric_last = categorybase_last.groupby('張地')['金額'].sum().sort_values(ascending=False)
        fabric_last2 = fabric_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        fabric_now.rename('今期', inplace=True)
        fabric_last.rename('前期', inplace=True)
        df_fabric = pd.concat([fabric_now, fabric_last], axis=1, join='outer')
        df_fabric = df_fabric.sort_values('今期', ascending=False)[:12]
        df_fabric = df_fabric.fillna(0)

        if 'ｱｰﾑﾁｪｱ' in df_fabric.index:
            df_fabric = df_fabric.drop(index='ｱｰﾑﾁｪｱ')

        #グラフ
        st.write('シリーズ別張地別売上(今期)')
        graph.make_bar_nowlast(df_fabric['今期'], df_fabric['前期'], df_fabric.index)

        col1, col2 = st.columns(2)
        with col1:
            # グラフ　張地別売り上げ
            st.write('張地別売上構成比(今期)')
            graph.make_pie(df_fabric['今期'], df_fabric.index)

        with col2:
            # グラフ　張地別売り上げ
            st.write('張地別売上構成比(前期)')
            graph.make_pie(df_fabric['前期'], df_fabric.index)

    def series_sales():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        st.caption('下段 構成比')
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]

        # ***シリーズ別売り上げ ***
        series_now = categorybase_now.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False)
        series_last = categorybase_last.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False)
        series_now2 = series_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        series_last2 = series_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        series_now.rename('今期', inplace=True)
        series_last.rename('前期', inplace=True)
        df_series = pd.concat([series_now, series_last], axis=1, join='outer')
        df_series = df_series.fillna(0)
        df_seires = df_series.sort_values('今期', ascending=False)[:12]

        #グラフ
        st.markdown('#### シリーズ別売上')
        graph.make_bar_nowlast(df_seires['今期'], df_seires['前期'], df_seires.index)

        col1, col2 = st.columns(2)


        with col1:
            st.write('シリーズ別売り上げ構成比(今期)')
            graph.make_pie(df_series['今期'], df_series.index)
        with col2:
            st.write('シリーズ別売り上げ構成比(前期)')
            graph.make_pie(df_series['前期'], df_series.index)


    def series_count():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        st.caption('下段 構成比')
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]

        # ***シリーズ別売り上げ ***
        series_now = categorybase_now.groupby('シリーズ名')['数量'].sum().sort_values(ascending=False).head(12) #降順
        series_last = categorybase_last.groupby('シリーズ名')['数量'].sum().sort_values(ascending=False).head(12) #降順
        series_now2 = series_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        series_last2 = series_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        # *** DF シリーズ別売り上げ ***

        series_now.rename('今期', inplace=True)
        series_last.rename('前期', inplace=True)
        df_series = pd.concat([series_now, series_last], axis=1, join='outer')
        df_series = df_series.fillna(0)
        df_seires = df_series.sort_values('今期', ascending=False)[:12]

        #グラフ
        st.markdown('#### シリーズ別数量')
        graph.make_bar_nowlast(df_seires['今期'], df_seires['前期'], df_seires.index)

        col1, col2 = st.columns(2)


        with col1:
            st.write('シリーズ別数量構成比(今期)')
            graph.make_pie(df_series['今期'], df_series.index)
        with col2:
            st.write('シリーズ別数量構成比(前期)')
            graph.make_pie(df_series['前期'], df_series.index)


    def series_col_fab():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_now = categorybase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除
        categorybase_now['シリーズ名2'] = \
            categorybase_now['シリーズ名'] + '/' + categorybase_now['塗色CD'] + '/' + categorybase_now['張地'] 

        # categorybase_now2 = categorybase_now.groupby(['シリーズ名', '塗色CD', '張地'])['数量'].sum().sort_values(ascending=False).head(20)
        categorybase_now2 = \
            categorybase_now.groupby('シリーズ名2')['数量'].sum().sort_values(ascending=False).head(20)
        
        st.markdown('#### 売れ筋ランキング')
        graph.make_bar(categorybase_now2, categorybase_now2.index)


    def series_col_fab2_sales():

        with st.form('入力フォーム'):
            # *** selectbox 商品分類2***
            category = ['ダイニングチェア', 'リビングチェア']
            option_category = st.selectbox(
                'category:',
                category,   
            ) 
            
            # *** selectbox シリーズ名***
            series_list = df_now['シリーズ名'].unique()
            option_series = st.selectbox(
                'series:',
                series_list,   
            )  

            # *** selectbox 塗色名***
            color_list = df_now['塗色CD'].unique()
            option_color = st.selectbox(
                'color:',
                color_list,   
            )

            submitted = st.form_submit_button('submit')
            
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        seriesbase_now = categorybase_now[categorybase_now['シリーズ名']==option_series]    

        colorbase_now = seriesbase_now[seriesbase_now['塗色CD']==option_color]
        colorbase_now = colorbase_now[colorbase_now['張地'] != '']
        # colorbase_now = colorbase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除

        colorbase_now2 = colorbase_now.groupby(['張地'])['金額'].sum().sort_values(ascending=False).head(10)

        st.markdown('#### 張地売り上げ 商品分類/シリース別/塗色別(今期)')
        graph.make_bar(colorbase_now2, colorbase_now2.index)

        st.caption('※ダイニングチェアの場合、張地空欄は板座')

    def series_col_fab2_count():

        with st.form('入力フォーム'):
            # *** selectbox 商品分類2***
            category = ['ダイニングチェア', 'リビングチェア']
            option_category = st.selectbox(
                'category:',
                category,   
            ) 
            
            # *** selectbox シリーズ名***
            series_list = df_now['シリーズ名'].unique()
            option_series = st.selectbox(
                'series:',
                series_list,   
            )  

            # *** selectbox 塗色名***
            color_list = df_now['塗色CD'].unique()
            option_color = st.selectbox(
                'color:',
                color_list,   
            )

            submitted = st.form_submit_button('submit')
            
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        seriesbase_now = categorybase_now[categorybase_now['シリーズ名']==option_series]    

        colorbase_now = seriesbase_now[seriesbase_now['塗色CD']==option_color]
        colorbase_now = colorbase_now[colorbase_now['張地'] != '']
        # colorbase_now = colorbase_now.dropna(subset=['張地']) #['張地']に空欄がある場合行削除

        colorbase_now2 = colorbase_now.groupby(['張地'])['数量'].sum().sort_values(ascending=False).head(10)

        st.markdown('#### 張地数量 商品分類/シリース別/塗色別(今期)')
        graph.make_bar(colorbase_now2, colorbase_now2.index)

        st.caption('※ダイニングチェアの場合、張地空欄は板座')

    def main():
        # アプリケーション名と対応する関数のマッピング
        apps = {
            '-': none,
            '売上 前年比●': earnings_comparison_year,
            '売上 月別': earnings_comparison_month,
            '比率 リビング/ダイニング●' :living_dining_latio,
            'LD シリーズ別/売上構成比': living_dining_comparison_ld,
            '比率 北海道工場/節材/国産材●': hokkaido_fushi_kokusanzai,
            '粗利/売上 きつつき森の研究所●': profit_aroma,
            '塗色別 売上/構成比 (商品分類別)●': color,
            '張地別 売上/構成比 (商品分類別)●': fabric,
            'シリーズ別 売上/構成比●': series_sales,
            'シリーズ別 数量/構成比●': series_count,
            '売れ筋ランキング 商品分類別/シリーズ別 塗色/張地●': series_col_fab,
            '張地ランキング 売上●': series_col_fab2_sales,
            '張地ランキング 数量●': series_col_fab2_count
            
        }
        selected_app_name = st.selectbox(label='分析項目の選択',
                                                options=list(apps.keys()), key='tab1')                                  

        # 選択されたアプリケーションを処理する関数を呼び出す
        render_func = apps[selected_app_name]
        render_func()

    if __name__ == '__main__':
        main()

#************************************************************************************************tab2
with tab2:
    st.markdown('### ■ 得意先一覧')

    def none2():
        st.info('分析項目を選択してください')

    def earnings_comparison():
        customer_list = df_now['得意先名'].unique()

        index = []
        earnings_now = []
        earnings_last = []
        comparison_rate = []
        comparison_diff = []

        for customer in customer_list:
            index.append(customer)
            cust_earnings_total_now = df_now[df_now['得意先名']==customer]['金額'].sum()
            cust_earnings_total_last = df_last[df_last['得意先名']==customer]['金額'].sum()
            earnings_rate_culc = f'{cust_earnings_total_now/cust_earnings_total_last*100: 0.1f} %'
            comaparison_diff_culc = cust_earnings_total_now - cust_earnings_total_last

            earnings_now.append(cust_earnings_total_now)
            earnings_last.append(cust_earnings_total_last)
            comparison_rate.append(earnings_rate_culc)
            comparison_diff.append(comaparison_diff_culc)
        earnings_comparison_list = pd.DataFrame(list(zip(earnings_now, earnings_last, comparison_rate, comparison_diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])    
        st.caption('列名クリックでソート')
        st.dataframe(earnings_comparison_list)

    def earnings_comparison_month():

        #年月表記
        df_now2 = df_now.sort_values('受注日')
        df_now2['受注年月'] = df_now2['受注日'].dt.strftime("%Y-%m")

        df_last2 = df_last.sort_values('受注日')
        df_last2['受注年月'] = df_last2['受注日'].dt.strftime("%Y-%m")

        #index用monthリスト
        month_list = df_now2['受注年月'].unique()

        # *** selectbox 得意先名***
        option_month = st.selectbox(
        '受注月:',
        month_list,   
        ) 

        temp_year = int(option_month.split('-')[0])
        temp_year = temp_year - 1
        option_month_last = str(temp_year) + '-' + option_month.split('-')[1]
        customer_list = df_now['得意先名'].unique()

        index = []
        earnings_now = []
        earnings_last = []
        comparison_rate = []
        comparison_diff = []

        df_now_month = df_now2[df_now2['受注年月']==option_month]
        df_last_month = df_last2[df_last2['受注年月']==option_month_last]

        earnings_now_total = df_now_month['金額'].sum()
        earnings_last_total = df_last_month['金額'].sum()
        comparison_rate_total = f'{earnings_now_total/earnings_last_total *100: 0.1f} %'
        comparison_diff_total =earnings_now_total - earnings_last_total
        data_list = [earnings_now_total, earnings_last_total, comparison_rate_total, comparison_diff_total]
        earnings_comparison_total_list = pd.DataFrame(data=[[earnings_now_total, earnings_last_total, comparison_rate_total, comparison_diff_total]], columns=['今期', '前期', '対前年比', '対前年差'])
        st.markdown("###### 合計")
        st.table(earnings_comparison_total_list)

        for customer in customer_list:
            index.append(customer)
            cust_earnings_total_now_month = df_now_month[df_now_month['得意先名']==customer]['金額'].sum()
            cust_earnings_total_last_month = df_last_month[df_last_month['得意先名']==customer]['金額'].sum()
            earnings_rate_culc = f'{cust_earnings_total_now_month/cust_earnings_total_last_month *100: 0.1f} %'
            comaparison_diff_culc = cust_earnings_total_now_month - cust_earnings_total_last_month

            earnings_now.append(cust_earnings_total_now_month)
            earnings_last.append(cust_earnings_total_last_month)
            comparison_rate.append(earnings_rate_culc)
            comparison_diff.append(comaparison_diff_culc)
        earnings_comparison_list = pd.DataFrame(list(zip(earnings_now, earnings_last, comparison_rate, comparison_diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
        st.markdown("###### 得意先別")  
        st.dataframe(earnings_comparison_list)
        st.caption('列名クリックでソート')


    def ld_earnings_comp():
        customer_list = df_now['得意先名'].unique()

        index = []
        l_earnings = [] #リニング売り上げ
        l_comp = [] #リビング比率

        d_earnings = [] #ダイニング売り上げ
        d_comp = [] #ダイニング比率

        o_earnings = [] #その他売り上げ
        o_comp = [] #その他比率

        for customer in customer_list:
            index.append(customer)

            df_now_cust = df_now[df_now['得意先名']==customer]

            df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

            df_now_cust_sum_l = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
            l_earnings.append('{:,}'.format(df_now_cust_sum_l))
            l_comp_culc = f'{df_now_cust_sum_l/df_now_cust_sum*100:0.1f} %'
            l_comp.append(l_comp_culc)

            df_now_cust_sum_d = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
            d_earnings.append('{:,}'.format(df_now_cust_sum_d))
            d_comp_culc = f'{df_now_cust_sum_d/df_now_cust_sum*100:0.1f} %'
            d_comp.append(d_comp_culc)

            df_now_cust_sum_o = df_now_cust[df_now_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子', 'デスク', '小物・その他'])]['金額'].sum()
            o_earnings.append('{:,}'.format(df_now_cust_sum_o))
            o_comp_culc = f'{df_now_cust_sum_o/df_now_cust_sum*100:0.1f} %'
            o_comp.append(o_comp_culc)

        st.write('構成比')
        df_earnings_list = pd.DataFrame(list(zip(l_comp, d_comp, o_comp)), index=index, columns=['L', 'D', 'その他'])
        st.dataframe(df_earnings_list)
        st.caption('列名クリックでソート')

    def hokkaido_fiushi_kokusan_comp(): #作成中
        customer_list = df_now['得意先名'].unique()

        index = []
        hokkaido = [] #北海道売り上げ
        hokkaido_comp = [] #北海道比率

        fushi = [] #節売り上げ
        fushi_comp = [] #節比率

        kokusan = [] #国産売り上げ
        kokusan_comp = [] #国産比率

        for customer in customer_list:
            index.append(customer)

            df_now_cust = df_now[df_now['得意先名']==customer]

            df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

            now_cust_sum_h = df_now_cust[df_now_cust['出荷倉庫']==510]['金額'].sum()
            hokkaido.append('{:,}'.format(now_cust_sum_h))
            hokkaido_comp_culc = f'{now_cust_sum_h/df_now_cust_sum*100:0.1f} %'
            hokkaido_comp.append(hokkaido_comp_culc)

            #節あり材
            now_cust_sum_fushi = df_now_cust[df_now_cust['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
            '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
            fushi.append('{:,}'.format(now_cust_sum_fushi))
            fushi_comp_culc = f'{now_cust_sum_fushi/df_now_cust_sum*100:0.1f} %'
            fushi_comp.append(fushi_comp_culc)

            #国産材
            kokusanzai_now1 = df_now_cust[df_now_cust['シリーズ名'].isin([\
                '北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', '杉座', 'ｿﾌｨｵ SUGI', '風のうた',\
                'Kinoe', 'SUWARI', 'KURINOKI'\
                    ])]['金額'].sum() #SHSカバ拾えていない

            kokusanzai_now2 = df_now_cust[df_now_cust['商品コード2'].isin([\
                'SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C',\
                    'KD201AM', 'KD201AK', 'KD201AC'\
                        ])]['金額'].sum()
        
            
            kokusanzai_now3 = df_now_cust[df_now_cust['商品コード3']=='HJ']['金額'].sum()

            kokusanzai_now_t = kokusanzai_now1 + kokusanzai_now2 + kokusanzai_now3

            kokusan.append('{:,}'.format(kokusanzai_now_t))
            kokusan_comp_culc = f'{kokusanzai_now_t/df_now_cust_sum*100:0.1f} %'
            kokusan_comp.append(kokusan_comp_culc)

        #分類の詳細
        with st.expander('分類の詳細'):
            st.write('【節あり】森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
            st.write('【国産材1】北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた\
                Kinoe/SUWARI/KURINOKI')
            st.write('【国産材2】SG261M/SG261K/SG261C/SG261AM/SG261AK/SG261AC/KD201M/KD201K/KD201C\
                    KD201AM/KD201AK/KD201AC') 
        st.write('構成比')                
        df_comp_list = pd.DataFrame(list(zip(hokkaido_comp, fushi_comp, kokusan_comp)), index=index, columns=['北海道工場', '節材', '国産材'])
        st.dataframe(df_comp_list, width=2000)
        st.caption('列名クリックでソート')

    def profit_aroma():
        customer_list = df_now['得意先名'].unique()

        index_list = []
        profit_list = [] #粗利
        profit_ratio_list = [] #粗利率
        aroma_list = [] #アロマ売り上げ

        for customer in customer_list:
            index_list.append(customer)

            df_now_cust = df_now[df_now['得意先名']==customer]

            df_now_cust_sum = df_now_cust['金額'].sum() #得意先売り上げ合計

            now_cust_sum_profit = df_now_cust['原価金額'].sum()
            profit_ratio_culc = f'{(df_now_cust_sum - now_cust_sum_profit)/df_now_cust_sum*100:0.1f} %'
            profit_ratio_list.append(profit_ratio_culc)

            profit_list.append(df_now_cust_sum - now_cust_sum_profit)

            now_cust_sum_aroma = df_now_cust[\
                df_now_cust['シリーズ名'].isin(['Essenntial Oil & Aroma Goods'])]['金額'].sum()
            aroma_list.append('{:,}'.format(now_cust_sum_aroma))

        df_comp_list = pd.DataFrame(list(zip(profit_ratio_list, profit_list, aroma_list)),\
            index=index_list, columns=['粗利率', '粗利額','アロマ'])
        st.dataframe(df_comp_list)
        st.caption('列名クリックでソート')
                

    def main():
        # アプリケーション名と対応する関数のマッピング
        apps = {
            '-': none2,
            '売上/前年比(累計)●': earnings_comparison,
            '売上/前年比(月毎)●': earnings_comparison_month,
            '構成比 LD●': ld_earnings_comp,
            '構成比 北海道/節/国産●': hokkaido_fiushi_kokusan_comp,
            '比率 粗利/アロマ関連●': profit_aroma,
            
        }
        selected_app_name = st.selectbox(label='分析項目の選択',
                                                options=list(apps.keys()), key='tab2')


        # 選択されたアプリケーションを処理する関数を呼び出す
        render_func = apps[selected_app_name]
        render_func()

    if __name__ == '__main__':
        main()

#**********************************************************************************************tab3
with tab3:
    st.markdown('### ■ 得意先/個別')
    st.markdown('#### 得意先の選択')
    cust_text = st.text_input('得意先名の一部を入力 例）仙台港')

    cust_list = []
    for cust_name in df_now['得意先名'].unique():
        if cust_text in cust_name:
            cust_list.append(cust_name)       

    cust_list.insert(0, '--')
    if cust_list != '':
        # selectbox target ***
        option_customer = st.selectbox('得意先を選択:', cust_list, key='tab31') 


    #************************累計売上
    #年月表記
    df_now2 = df_now.sort_values('受注日')
    df_now2['受注年月'] = df_now2['受注日'].dt.strftime("%Y-%m")

    df_last2 = df_last.sort_values('受注日')
    df_last2['受注年月'] = df_last2['受注日'].dt.strftime("%Y-%m")

    #index用monthリスト
    month_list = df_now2['受注年月'].unique()
    
    
    df_now_cust =df_now2[df_now2['得意先名']==option_customer]
    df_last_cust =df_last2[df_last2['得意先名']==option_customer]
    now_cust_total = df_now_cust['金額'].sum()
    last_cust_total = df_last_cust['金額'].sum()

    def none3():
        st.info('分析項目を選択してくださしてください')

    def earnings_comparison_year():

        total_comparison = f'{now_cust_total / last_cust_total * 100: 0.1f} %'
        diff = '{:,}'.format(now_cust_total - last_cust_total)
        
        with st.expander('詳細', expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric('今期売上', value= '{:,}'.format(now_cust_total), delta=diff)
            with col2:
                st.metric('前期売上', value= '{:,}'.format(last_cust_total))
            with col3:
                st.metric('対前年比', value= total_comparison)

        val_list = [now_cust_total, last_cust_total]
        x_list = ['今期', '前期']
        st.markdown('#### 売上（累計）')
        graph.make_bar(val_list, x_list)        

    def earnings_comparison_month():

        
        columns_list = ['今期', '前期', '対前年差', '対前年比']
        df_now_cust = df_now2[df_now2['得意先名']==option_customer]
        df_last_cust = df_last2[df_last2['得意先名']==option_customer]

        earnings_now = []
        earnings_last = []
        earnings_diff = []
        earnings_rate = []

        for (month_now, month_last) in zip(df_now2['受注年月'].unique(), df_last2['受注年月'].unique()):
            earnings_month_now = df_now_cust[df_now_cust['受注年月'].isin([month_now])]['金額'].sum()
            earnings_month_last = df_last_cust[df_last_cust['受注年月'].isin([month_last])]['金額'].sum()
            earnings_diff_culc = earnings_month_now - earnings_month_last
            earnings_rate_culc = f'{earnings_month_now / earnings_month_last * 100: 0.1f} %'

            earnings_now.append('{:,}'.format(earnings_month_now))
            earnings_last.append('{:,}'.format(earnings_month_last))
            earnings_diff.append('{:,}'.format(earnings_diff_culc))
            earnings_rate.append(earnings_rate_culc)

        df_earnings_month = pd.DataFrame(list(zip(earnings_now, earnings_last, earnings_diff, earnings_rate)), columns=columns_list, index=month_list)
        
        with st.expander('詳細', expanded=False):
            st.caption('受注月ベース')
            st.table(df_earnings_month)

        #グラフ用にintのデータを用意
        df_earnings_month2 = df_earnings_month.copy()
        df_earnings_month2['今期'] = df_earnings_month2['今期'].apply(lambda x: int(x.replace(',', '')))
        df_earnings_month2['前期'] = df_earnings_month2['前期'].apply(lambda x: int(x.replace(',', '')))


        #可視化
        x_list = ['今期', '前期']
        st.markdown('#### 月別売上')

        df_list = [df_earnings_month2['今期'], df_earnings_month2['前期']]
        graph.make_line(df_list, x_list, month_list)

    def mean_earning_month():
        st.write('#### 平均成約単価')

        columns_list = ['今期', '前期', '対前年差', '対前年比']
        df_now_cust = df_now2[df_now2['得意先名']==option_customer]
        df_last_cust = df_last2[df_last2['得意先名']==option_customer]

        order_num_now = []
        for num in df_now_cust['伝票番号']:
            num2 = num.split('-')[0]
            order_num_now.append(num2)
        df_now_cust['order_num'] = order_num_now

        order_num_last = []
        for num in df_last_cust['伝票番号']:
            num2 = num.split('-')[0]
            order_num_last.append(num2)
        df_last_cust['order_num'] = order_num_last


        earnings_now = []
        earnings_last = []
        earnings_diff = []
        earnings_rate = []

        for (month_now, month_last) in zip(df_now2['受注年月'].unique(), df_last2['受注年月'].unique()):
            earnings_month_now = df_now_cust[df_now_cust['受注年月'].isin([month_now])]
            order_sum_now = earnings_month_now.groupby('order_num')['金額'].sum()
            order_mean_now = order_sum_now.mean()

            earnings_month_last = df_last_cust[df_last_cust['受注年月'].isin([month_last])]
            order_sum_last = earnings_month_last.groupby('order_num')['金額'].sum()
            order_mean_last = order_sum_last.mean()

            order_mean_diff = order_mean_now - order_mean_last
            if order_mean_last == 0:
                order_mean_rate = '0%'
            else:
                order_mean_rate = f'{(order_mean_now / order_mean_last)*100: 0.1f} %'
            
            earnings_now.append(order_mean_now)
            earnings_last.append(order_mean_last)
            earnings_diff.append(order_mean_diff)
            earnings_rate.append(order_mean_rate)

        df_mean_earninngs_month = pd.DataFrame(list(zip(earnings_now, earnings_last, earnings_diff, earnings_rate)), \
                                               columns=columns_list, index=month_list)
        st.caption('受注月ベース')

        col1, col2 = st.columns(2)

        with col1:
            diff = int(df_mean_earninngs_month['今期'].mean()) - int(df_mean_earninngs_month['前期'].mean())
            st.metric('今期平均', value='{:,}'.format(int(df_mean_earninngs_month['今期'].mean())), \
                delta='{:,}'.format(diff))

        with col2:
            st.metric('前期平均', value='{:,}'.format(int(df_mean_earninngs_month['前期'].mean()))) 

        df_mean_earninngs_month.fillna(0, inplace=True)
        df_mean_earninngs_month['今期'] = \
            df_mean_earninngs_month['今期'].map(lambda x: '{:,}'.format(int(x))) 
        df_mean_earninngs_month['前期'] = \
            df_mean_earninngs_month['前期'].map(lambda x: '{:,}'.format(int(x))) 
        df_mean_earninngs_month['対前年差'] = \
            df_mean_earninngs_month['対前年差'].map(lambda x: '{:,}'.format(int(x)))   
        
        with st.expander('詳細', expanded=False):
            st.table(df_mean_earninngs_month) 

        #グラフ用にintのデータを用意
        df_mean_earninngs_month2 = df_mean_earninngs_month.copy()
        df_mean_earninngs_month2['今期'] = \
            df_mean_earninngs_month2['今期'].apply(lambda x: int(x.replace(',', '')))
        df_mean_earninngs_month2['前期'] = \
            df_mean_earninngs_month2['前期'].apply(lambda x: int(x.replace(',', '')))


        #可視化
        st.markdown('#### 平均成約単価')
        df_list = [df_mean_earninngs_month2['今期'], df_mean_earninngs_month2['前期']]
        x_list = ['今期', '前期']
        graph.make_line(df_list, x_list, month_list)       
        
    def living_dining_comparison():
        st.markdown('##### LD 前年比/構成比')

        #living
        living_now = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        living_last = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

        l_diff = living_now-living_last
        l_ratio = f'{living_now/living_last*100:0.1f} %'

        #dining
        dining_now = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        dining_last = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()

        #else
        else_now = df_now_cust[df_now_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子','デスク', '小物・その他'])]['金額'].sum()
        else_last = df_last_cust[df_last_cust['商品分類名2'].isin(['キャビネット類', 'その他テーブル', '雑品・特注品', 'その他椅子','デスク', '小物・その他'])]['金額'].sum()

        d_diff = dining_now-dining_last
        d_ratio = f'{dining_now/dining_last*100:0.1f} %'

        #グラフ
        now_list = [living_now, dining_now, else_now]
        last_list = [living_last, dining_last, else_last]
        x_list = ['リビング', 'ダイニング', 'その他']
        graph.make_bar_nowlast(now_list, last_list, x_list)

        col1, col2 = st.columns(2)
        with col1:
            st.caption(f'対前年差 {l_diff}')
            st.caption(f'対前年比 {l_ratio}')
            st.caption('クッション/リビングチェア/リビングテーブル')

        with col2:
            st.caption(f'対前年差 {d_diff}')
            st.caption(f'対前年比 {d_ratio}')
            st.caption('ダイニングテーブル/ダイニングチェア/ベンチ')   

        with col1:
            comp_now_list = [living_now, dining_now, else_now]
            comp_now_index = ['リビング', 'ダイニング', 'その他']
            comp_now_columns = ['分類']
            df_comp_now = pd.DataFrame(comp_now_index, columns=comp_now_columns)
            df_comp_now['金額'] = comp_now_list

            #グラフ
            st.markdown('###### LD比率(今期)')
            graph.make_pie(df_comp_now['金額'], df_comp_now['分類'])

        with col2:
            comp_last_list = [living_last, dining_last, else_last]
            comp_last_index = ['リビング', 'ダイニング', 'その他']
            comp_last_columns = ['分類']
            df_comp_last = pd.DataFrame(comp_last_index, columns=comp_last_columns)
            df_comp_last['金額'] = comp_last_list

            #グラフ
            st.markdown('###### LD比率(前期)')
            graph.make_pie(df_comp_last['金額'], df_comp_last['分類'])

    def living_dining_comparison_ld():

        # *** selectbox LD***
        category = ['リビング', 'ダイニング']
        option_category = st.selectbox('category:', category, key='ldcl') 
        if option_category == 'リビング':
            df_now_cust_cate = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
            df_last_cust_cate = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        elif option_category == 'ダイニング':
            df_now_cust_cate = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
            df_last_cust_cate = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]

        index = []
        now_result = []
        last_result = []
        diff = []
        ratio = []
        series_list = df_now_cust_cate['シリーズ名'].unique()
        
        for series in series_list:
            index.append(series)
            now_culc = df_now_cust_cate[df_now_cust_cate['シリーズ名']==series]['金額'].sum()
            last_culc = df_last_cust_cate[df_last_cust_cate['シリーズ名']==series]['金額'].sum()
            now_result.append(now_culc)
            last_result.append(last_culc)
            diff_culc = '{:,}'.format(now_culc - last_culc)
            diff.append(diff_culc)
            ratio_culc = f'{now_culc/last_culc*100:0.1f} %'
            ratio.append(ratio_culc)
        df_result = pd.DataFrame(list(zip(now_result, last_result, ratio, diff)), index=index, columns=['今期', '前期', '対前年比', '対前年差'])
        
        with st.expander('一覧', expanded=False):
            st.dataframe(df_result)
            st.caption('列名クリックでソート')

        st.markdown('#### シリーズ別売上') 
        graph.make_bar_nowlast(df_result['今期'], df_result['前期'], df_result.index) 
        
        #**********構成比円グラフ***************
        st.markdown('##### シリーズ別構成比/今期')
        graph.make_pie(df_result['今期'], df_result.index)

        st.markdown('##### シリーズ別構成比/前期')
        graph.make_pie(df_result['前期'], df_result.index)
    

    def series():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        st.caption('構成比は下段')
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]
        categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
        categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

        # ***シリーズ別売り上げ ***
        series_now = categorybase_cust_now.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
        series_now2 = series_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        series_last = categorybase_cust_last.groupby('シリーズ名')['金額'].sum().sort_values(ascending=False).head(12) #降順
        series_last2 = series_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        graph.make_bar_nowlast(series_now, series_last, series_now.index)

        st.markdown('##### シリーズ別売り上げ構成比/今期')
        graph.make_pie(series_now, series_now.index)

        st.markdown('##### シリーズ別売り上げ構成比/前期')
        graph.make_pie(series_last, series_last.index)


    def item_count_category():
        # *** selectbox 得意先名***
        categories = df_now_cust['商品分類名2'].unique()
        option_categories = st.selectbox(
        '商品分類名2:',
        categories,   
        )    

        index = []
        count_now = []
        count_last = []
        diff = []

        df_now_cust_categories = df_now_cust[df_now_cust['商品分類名2']==option_categories]
        df_last_cust_categories = df_last_cust[df_last_cust['商品分類名2']==option_categories]
        series_list = df_now_cust[df_now_cust['商品分類名2']==option_categories]['シリーズ名'].unique()
        for series in series_list:
            index.append(series)
            month_len = len(df_now2['受注年月'].unique())
            df_now_cust_categories_count_culc = \
                df_now_cust_categories[df_now_cust_categories['シリーズ名']==series]['数量'].sum()
            df_last_cust_categories_count_culc = \
                df_last_cust_categories[df_last_cust_categories['シリーズ名']==series]['数量'].sum()
            count_now.append(f'{df_now_cust_categories_count_culc/month_len: 0.1f}')
            count_last.append(f'{df_last_cust_categories_count_culc/month_len: 0.1f}')
            diff.append(\
                f'{(df_now_cust_categories_count_culc/month_len) - (df_last_cust_categories_count_culc/month_len):0.1f}')

        with st.expander('一覧', expanded=False):
            st.write('回転数/月平均')
            df_item_count = pd.DataFrame(list(zip(count_now, count_last, diff)), index=index, columns=['今期', '前期', '対前年差'])
            st.table(df_item_count) #列幅問題未解決 

        #*********前年比棒グラフ**************
        df_item_count2 = df_item_count.copy()
        df_item_count2['今期'] = df_item_count2['今期'].apply(lambda x: float(x))
        df_item_count2['前期'] = df_item_count2['前期'].apply(lambda x: float(x))

        graph.make_bar_nowlast_float(df_item_count2['今期'], df_item_count2['前期'], df_item_count2.index)

    def category_count_month():
        #　回転数 商品分類別 月毎
        # *** selectbox シリーズ名***
        category_list = df_now_cust['商品分類名2'].unique()
        option_category = st.selectbox(
        '商品分類名:',
        category_list,   
        ) 
        df_now_cust_category = df_now_cust[df_now_cust['商品分類名2']==option_category]

        count_now = []
        series_list = df_now_cust_category['シリーズ名'].unique()
        df_count = pd.DataFrame(index=series_list)
        for month in df_now2['受注年月'].unique():
            for series in series_list:
                df_now_cust_category_ser = df_now_cust_category[df_now_cust_category['シリーズ名']==series]
                count = df_now_cust_category_ser[df_now_cust_category_ser['受注年月']==month]['数量'].sum()
                count_now.append(count)
            df_count[month] = count_now
            count_now = []

        with st.expander('一覧', expanded=False): 
            st.caption('今期')
            st.write(df_count)
    
        #可視化
        df_count2 = df_count.T #index月　col　seirs名に転置
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()
        #今期のグラフの追加
        for col in df_count2.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_now2['受注年月'].unique(),
                    y=df_count2[col],
                    mode = 'lines+markers+text', #値表示
                    text=df_count2[col],
                    textposition="top center", 
                    name=col)
            )

        #レイアウト設定     
        fig.update_layout(
            title='月別回転数',
            showlegend=True #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True)       

    def hokkaido_fushi_kokusanzai():
        # *** 北海道比率　節材比率　国産材比率 ***
        col1, col2, col3 = st.columns(3)
        cust_now = df_now[df_now['得意先名']== option_customer]
        cust_last = df_last[df_last['得意先名']== option_customer]
        total_now = cust_now['金額'].sum()
        total_last = cust_last['金額'].sum()

        #分類の詳細
        with st.expander('分類の詳細'):
            st.write('【節あり】森のことば/LEVITA (ﾚｳﾞｨﾀ)/森の記憶/とき葉/森のことばIBUKI/森のことば ウォルナット')
            st.write('【国産材1】北海道民芸家具/HIDA/Northern Forest/北海道HMその他/杉座/ｿﾌｨｵ SUGI/風のうた\
                Kinoe/SUWARI/KURINOKI')
            st.write('【国産材2】SG261M/SG261K/SG261C/SG261AM/SG261AK/SG261AC/KD201M/KD201K/KD201C\
                    KD201AM/KD201AK/KD201AC')
        with col1:
            hokkaido_now = cust_now[cust_now['出荷倉庫']==510]['金額'].sum()
            hokkaido_last = cust_last[cust_last['出荷倉庫']==510]['金額'].sum()
            hokkaido_diff = f'{(hokkaido_now/total_now*100) - (hokkaido_last/total_last*100):0.1f} %'

            st.metric('北海道工場比率', value=f'{hokkaido_now/total_now*100: 0.1f} %', delta=hokkaido_diff) #小数点以下1ケタ
            st.caption(f'前年 {hokkaido_last/total_last*100: 0.1f} %')

        with col2:
            fushi_now = cust_now[cust_now['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
            '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
            fushi_last = cust_last[cust_last['シリーズ名'].isin(['森のことば', 'LEVITA (ﾚｳﾞｨﾀ)', '森の記憶', 'とき葉', 
            '森のことばIBUKI', '森のことば ウォルナット'])]['金額'].sum()
            # sdソファ拾えていない isin その値を含む行　true
            fushi_diff = f'{(fushi_now/total_now*100) - (fushi_last/total_last*100):0.1f} %'
            st.metric('節材比率', value=f'{fushi_now/total_now*100: 0.1f} %', delta=fushi_diff) #小数点以下1ケタ
            st.caption(f'前年 {fushi_last/total_last*100:0.1f} %')

        with col3:
            kokusanzai_now1 = cust_now[cust_now['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
            '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない
            kokusanzai_last1 = cust_last[cust_last['シリーズ名'].isin(['北海道民芸家具', 'HIDA', 'Northern Forest', '北海道HMその他', 
            '杉座', 'ｿﾌｨｵ SUGI', '風のうた', 'Kinoe', 'SUWARI', 'KURINOKI'])]['金額'].sum() #SHSカバ拾えていない

            kokusanzai_now2 = cust_now[cust_now['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
            kokusanzai_last2 = cust_last[cust_last['商品コード2'].isin(['SG261M', 'SG261K', 'SG261C', 'SG261AM', 'SG261AK', 'SG261AC', 'KD201M', 'KD201K', 'KD201C', 'KD201AM', 'KD201AK', 'KD201AC'])]['金額'].sum()
            
            kokusanzai_now3 = cust_now[cust_now['商品コード3']=='HJ']['金額'].sum()
            kokusanzai_last3 = cust_last[cust_last['商品コード3']=='HJ']['金額'].sum()

            kokusanzai_now_t = kokusanzai_now1 + kokusanzai_now2 + kokusanzai_now3
            kokusanzai_last_t = kokusanzai_last1 + kokusanzai_last2 + kokusanzai_last3 

            with st.expander('数値', expanded=False):
                st.write('売上合計')
                st.write(total_now)
                st.write('国産材売上')
                st.write(kokusanzai_now_t)

            kokusanzai_diff = f'{(kokusanzai_now_t/total_now*100) - (kokusanzai_last_t/last_total*100): 0.1f} %'
            st.metric('国産材比率', value=f'{kokusanzai_now_t/total_now*100: 0.1f} %', delta=kokusanzai_diff) #小数点以下1ケタ
            st.caption(f'前年 {kokusanzai_last_t/total_last*100: 0.1f} %')

    def profit_aroma():
        col1, col2, col3 = st.columns(3)
        cust_now = df_now[df_now['得意先名']== option_customer]
        cust_last = df_last[df_last['得意先名']== option_customer]
        total_now = cust_now['金額'].sum()
        total_last = cust_last['金額'].sum()
        cost_now = cust_now['原価金額'].sum()
        cost_last = cust_last['原価金額'].sum()
        cost_last2 = f'{(total_last-cost_last)/total_last*100: 0.1f} %'
        diff = f'{((total_now-cost_now)/total_now*100) - ((total_last-cost_last)/total_last*100): 0.1f} %'
        with col1:
            st.metric('粗利率', value=f'{(total_now-cost_now)/total_now*100: 0.1f} %', delta=diff)
            st.caption(f'前年 {cost_last2}')

        with col2:
            profit = '{:,}'.format(total_now-cost_now)
            dif_profit = int((total_now-cost_now) - (total_last-cost_last))
            st.metric('粗利額', value=profit, delta=dif_profit)
            st.caption(f'前年 {total_last-cost_last}')

        with col3:
            aroma_now = cust_now[cust_now['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
            aroma_last = cust_last[cust_last['シリーズ名'].isin(['きつつき森の研究所'])]['金額'].sum()
            aroma_last2 = '{:,}'.format(aroma_last)
            aroma_diff = '{:,}'.format(aroma_now- aroma_last)
            st.metric('きつつき森の研究所関連', value=('{:,}'.format(aroma_now)), delta=aroma_diff)
            st.caption(f'前年 {aroma_last2}')

    def color():
        df_now_cust = df_now[df_now['得意先名']==option_customer]
        df_last_cust = df_last[df_last['得意先名']==option_customer]

        df_now_cust = df_now_cust.dropna(subset=['塗色CD'])
        df_last_cust = df_last_cust.dropna(subset=['塗色CD'])

        color_now = df_now_cust.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        color_last = df_last_cust.groupby('塗色CD')['金額'].sum().sort_values(ascending=False) #降順
        #color_last2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別売上')

        graph.make_bar_nowlast(color_now, color_last, color_now.index)

        st.markdown('###### 塗色別売上構成比/今期')
        graph.make_pie(color_now, color_now.index)

        st.markdown('###### 塗色別売上構成比/前期')
        graph.make_pie(color_last, color_last.index)



    def category_color():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]
        categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
        categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

        color_now = categorybase_cust_now.groupby('塗色CD')['数量'].sum().sort_values(ascending=False) #降順
        #color_now2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        color_last = categorybase_cust_last.groupby('塗色CD')['数量'].sum().sort_values(ascending=False) #降順
        #color_last2 = color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        st.markdown('###### 塗色別数量')
        graph.make_bar_nowlast(color_now, color_last, color_now.index)

        st.markdown('###### 塗色別数量構成比/今期')
        graph.make_pie(color_now, color_now.index)

        st.markdown('###### 塗色別数量構成比/前期')
        graph.make_pie(color_last, color_last.index)
                
    def category_fabric():
        # *** selectbox***
        category = ['ダイニングチェア', 'リビングチェア']
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]
        categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
        categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]
        categorybase_cust_now = categorybase_cust_now[categorybase_cust_now['張地'] != ''] #空欄を抜いたdf作成
        categorybase_cust_last = categorybase_cust_last[categorybase_cust_last['張地'] != '']


        # ***張地別数量 ***
        fabric_now = categorybase_cust_now.groupby('張地')['数量'].sum().sort_values(ascending=False).head(12) #降順
        #fabric2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        
        #脚カットの場合ファブリックの位置がずれる為、行削除
        for index in fabric_now.index:
            if index in ['ｾﾐｱｰﾑﾁｪｱ', 'ｱｰﾑﾁｪｱ', 'ﾁｪｱ']:
                fabric_now.drop(index=index, inplace=True)

        fabric_last = categorybase_cust_last.groupby('張地')['数量'].sum().sort_values(ascending=False).head(12) #降順
        #fabric2 = fabric_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる

        #脚カットの場合ファブリックの位置がずれる為、行削除
        for index in fabric_last.index:
            if index in ['ｾﾐｱｰﾑﾁｪｱ', 'ｱｰﾑﾁｪｱ', 'ﾁｪｱ']:
                fabric_last.drop(index=index, inplace=True)        

        st.markdown('###### 張地別数量')
        graph.make_bar_nowlast(fabric_now, fabric_last, fabric_now.index)

        st.markdown('###### 張地別数量構成比/今期')
        graph.make_pie(fabric_now, fabric_now.index)

        st.markdown('###### 張地別数量構成比/前期')
        graph.make_pie(fabric_last, fabric_last.index)

    def series_col_fab():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,   
        ) 
        categorybase_now = df_now[df_now['商品分類名2']==option_category]
        categorybase_last = df_last[df_last['商品分類名2']==option_category]
        categorybase_cust_now = categorybase_now[categorybase_now['得意先名']== option_customer]
        categorybase_cust_last = categorybase_last[categorybase_last['得意先名']== option_customer]

        # *** シリース別塗色別数量 ***
        series_color_now = categorybase_cust_now.groupby(['シリーズ名', '塗色CD', '張地'])['数量'].sum().sort_values(ascending=False).head(20) #降順
        series_color_now2 = series_color_now.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        
        # **シリーズ別塗色別数量 ***
        series_color_last = categorybase_cust_last.groupby(['シリーズ名', '塗色CD', '張地'])['数量'].sum().sort_values(ascending=False).head(20) #降順
        series_color_last2 = series_color_last.apply('{:,}'.format) #数値カンマ区切り　注意strになる　グラフ作れなくなる
        
        #数量2以上に限定
        df_series_color_now2 = series_color_now[series_color_now >=2]
        df_series_color_last2 = series_color_last[series_color_last >=2]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### 売れ筋ランキング 商品分類別(今期)')
            st.table(df_series_color_now2)
        with col2:
            st.write('###### 売れ筋ランキング 商品分類別(前期)')
            st.table(df_series_color_last2)

    def main():
        # アプリケーション名と対応する関数のマッピング
        apps = {
            '-': none3,
            '★売上 対前年比(累計)●': earnings_comparison_year,
            '★売上 対前年比(月毎)●': earnings_comparison_month,
            '平均成約単価': mean_earning_month,
            '★LD 前年比/構成比●': living_dining_comparison,
            '★LD シリーズ別/売上構成比●': living_dining_comparison_ld,
            '商品分類 シリーズ別 売上/構成比●': series,
            '★回転数 商品分類別●': item_count_category,
            '★回転数 商品分類別 月毎●': category_count_month,
            '★比率 北海道工場/節あり材/国産材●': hokkaido_fushi_kokusanzai, 
            '★比率 粗利/アロマ関連●': profit_aroma,
            '塗色別　売上構成比': color,
            '塗色別 数量/構成比/商品分類別●': category_color,
            '張地別 数量/構成比●': category_fabric,
            '売れ筋ランキング 商品分類別/塗色/張地●': series_col_fab
    
        }
        selected_app_name = st.selectbox(label='分析項目の選択',
                                                options=list(apps.keys()), key=tab3)


        # 選択されたアプリケーションを処理する関数を呼び出す
        render_func = apps[selected_app_name]
        render_func()

    if __name__ == '__main__':
        main()

#**********************************************************************************************tab4
with tab4:
    st.markdown('### ■ エリア')
    area_list = st.multiselect(
        '得意先を選択(複数)',
        df_now['得意先名'].unique())
    
    def none4():
        st.info('分析項目を選択してください')

    def sales():
        
        sum_list = []    
        for cust in area_list:
            now_cust_sum = df_now[df_now['得意先名']==cust]['金額'].sum()
            last_cust_sum = df_last[df_last['得意先名']==cust]['金額'].sum()
            temp_list = [last_cust_sum, now_cust_sum]
            sum_list.append(temp_list)

        df_results = pd.DataFrame(sum_list, columns=['前期', '今期'], index=area_list)
        df_results.loc['合計'] = df_results.sum()
        df_results['対前年比'] = df_results['今期'] / df_results['前期']
        df_results['対前年差'] = df_results['今期'] - df_results['前期']
        df_results = df_results.T

        ratio = '{:.2f}'.format(df_results.loc['対前年比', '合計'])
        diff = '{:,}'.format(int(df_results.loc['対前年差', '合計']))
        st.metric(label='対前年比', value=ratio, delta=diff)


        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()
        #今期のグラフの追加
        for col in df_results.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_results.index[:2],
                    y=df_results[col][:2],
                    mode = 'lines+markers+text', #値表示
                    text=round(df_results[col][:2]/10000),
                    textposition="top center",
                    name=col)
            )

        #レイアウト設定     
        fig.update_layout(
            title='エリア別売上（累計）',
            showlegend=True #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True) 

    def sales_month():
        #年月表記
        df_now2 = df_now.sort_values('受注日')
        df_now2['受注年月'] = df_now2['受注日'].dt.strftime("%Y-%m")

        df_last2 = df_last.sort_values('受注日')
        df_last2['受注年月'] = df_last2['受注日'].dt.strftime("%Y-%m")

        #index用monthリスト
        month_list = df_now2['受注年月'].unique()

        df_now_cust = df_now2[df_now2['得意先名'].isin(area_list)]
        df_last_cust = df_last2[df_last2['得意先名'].isin(area_list)]

        sum_list = []
        for (month_now, month_last) in zip(df_now2['受注年月'].unique(), df_last2['受注年月'].unique()):
            df_now_month = df_now_cust[df_now_cust['受注年月']==month_now]['金額'].sum()
            df_last_month = df_last_cust[df_last_cust['受注年月']==month_last]['金額'].sum()
            temp_list = [df_now_month, df_last_month]
            sum_list.append(temp_list)

        df_results = pd.DataFrame(sum_list, index=month_list, columns=['今期', '前期']) 

        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()
        #今期のグラフの追加
        for col in df_results.columns:
            fig.add_trace(
                go.Scatter(
                    x=month_list,
                    y=df_results[col],
                    mode = 'lines+markers+text', #値表示
                    text=round(df_results[col]/10000),
                    textposition="top center", 
                    name=col)
            )

        #レイアウト設定     
        fig.update_layout(
            title='エリア別売上',
            showlegend=True #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True) 

    def ld_comp():

        df_now_cust = df_now[df_now['得意先名'].isin(area_list)]
        df_last_cust = df_last[df_last['得意先名'].isin(area_list)]

        now_cust_sum_l = df_now_cust[df_now_cust['商品分類名2'].isin(\
            ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

        now_cust_sum_d = df_now_cust[df_now_cust['商品分類名2'].isin(\
            ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum() 

        last_cust_sum_l = df_last_cust[df_last_cust['商品分類名2'].isin(\
            ['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()

        last_cust_sum_d = df_last_cust[df_last_cust['商品分類名2'].isin(\
            ['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum() 
        temp_list = [[last_cust_sum_l, last_cust_sum_d], [now_cust_sum_l, now_cust_sum_d]] 

        df_results = pd.DataFrame(temp_list, index=['前期', '今期'], columns=['Living', 'Dining'])
        df_results.loc['対前年比'] = df_results.loc['今期'] / df_results.loc['前期']
        df_results.loc['対前年差'] = df_results.loc['今期'] - df_results.loc['前期']

        col1, col2 = st.columns(2)
        with col1:
            st.write('Living')
            ratio = '{:.2f}'.format(df_results.loc['対前年比', 'Living'])
            diff = '{:,}'.format(int(df_results.loc['対前年差', 'Living']))
            st.metric(label='対前年比', value=ratio, delta=diff)

        with col2:
            st.write('Dining')
            ratio = '{:.2f}'.format(df_results.loc['対前年比', 'Dining'])
            diff = '{:,}'.format(int(df_results.loc['対前年差', 'Dining']))
            st.metric(label='対前年比', value=ratio, delta=diff)    


        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()
        #今期のグラフの追加
        for col in df_results.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_results.index[:2], #対前年比,対前年差を拾わないように[:2]
                    y=df_results[col][:2],
                    mode = 'lines+markers+text', #値表示
                    text=round(df_results[col][:2]/10000),
                    textposition="top center", 
                    name=col)
            )

        #レイアウト設定     
        fig.update_layout(
            title='LD別売上',
            showlegend=True #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True)         

    def main():
        # アプリケーション名と対応する関数のマッピング
        apps = {
            '-': none4,
            '売上: 累計': sales,
            '売上: 月別': sales_month,
            'LD別売上: 累計': ld_comp

        }
        selected_app_name = st.selectbox(label='分析項目の選択',
                                                options=list(apps.keys()), key='tab4')


        # 選択されたアプリケーションを処理する関数を呼び出す
        render_func = apps[selected_app_name]
        render_func()

    if __name__ == '__main__':
        main()

#*****************************************************************************************tab5
with tab5:
    st.markdown('### ■ TIF')
    
    # オリジナル比率（全体）

    df_now2 = df_now.copy()
    df_last2 = df_last.copy()
    df_now2['得意先名'] = df_now2['得意先名'].fillna('nan')
    df_last2['得意先名'] = df_last2['得意先名'].fillna('nan')
    df_now2 = df_now2[df_now2['得意先名'].str.contains('㈱東京ｲﾝﾃﾘｱ')]
    df_last2 = df_last2[df_last2['得意先名'].str.contains('㈱東京ｲﾝﾃﾘｱ')]

    tif_now_total = df_now2['金額'].sum()
    tif_last_total = df_last2['金額'].sum()

    #年月表記
    df_now2 = df_now2.sort_values('受注日')
    df_now2['受注年月'] = df_now2['受注日'].dt.strftime("%Y-%m")

    df_last2 = df_last2.sort_values('受注日')
    df_last2['受注年月'] = df_last2['受注日'].dt.strftime("%Y-%m")

    #index用monthリスト
    month_list = df_now2['受注年月'].unique()

    def none5():
        st.info('分析項目を選択してください')
    
    def all_data():
        customer_list = df_now2['得意先名'].unique()

        index = []
        total_now = []
        total_last = []
        total_rate = []
        original_now = []
        original_last = []
        original_rate_now = []
        original_rate_last = []
        original_rate__diff = []

        for customer in customer_list:
            index.append(customer)
            df_now_cust = df_now2[df_now2['得意先名']==customer]
            df_last_cust = df_last2[df_last2['得意先名']==customer]

            total_sum_now = df_now_cust['金額'].sum()
            total_sum_last = df_last_cust['金額'].sum()
            total_sum_rate = round(total_sum_now / total_sum_last, 2) 
   

            cust_total_now = df_now_cust['金額'].sum()
            cust_total_last = df_last_cust['金額'].sum()
            original_now_culc = df_now_cust[df_now_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_last_culc = df_last_cust[df_last_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_rate_now_culc = round(original_now_culc / cust_total_now,2)
            original_rate_last_culc = round(original_last_culc / cust_total_last,2)
            original_rate_diff_culc = (original_now_culc / cust_total_now) - (original_last_culc / cust_total_last)

            total_now.append(total_sum_now)
            total_last.append(total_sum_last)
            total_rate.append(total_sum_rate)
            original_now.append(original_now_culc)
            original_last.append(original_last_culc)
            original_rate_now.append(original_rate_now_culc)
            original_rate_last.append(original_rate_last_culc)
            original_rate__diff.append(original_rate_diff_culc)
            
        original_rate_list = pd.DataFrame(list(zip(total_now, total_last, total_rate, original_now, original_last, \
                                                   original_rate_now, original_rate_last, original_rate__diff)), \
                                                    index=index, columns=[\
                                                        '今期売上', '前期売上', '対前年比',\
                                                        '今期O売上', '前期O売上', '今期O比率', '前期O比率', 'O対前年差'])
  
        st.dataframe(original_rate_list)


    def original_ratio():
        now_original_sum = df_now2[df_now2['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        last_original_sum = df_last2[df_last2['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()

        o_ratio_now = now_original_sum / tif_now_total
        o_ratio_last = last_original_sum / tif_last_total
        ratio_diff = f'{(o_ratio_now - o_ratio_last)*100:0.1f} %'

        st.markdown('###### オリジナル比率(全店)')
        
        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            graph.make_bar_nowlast_float([o_ratio_now], [o_ratio_last], ['オリジナル比率'])
        with col2:
            st.metric('今期', value=f'{o_ratio_now*100: 0.1f} %', delta=ratio_diff)
        with col3:
            st.metric('前期', value=f'{o_ratio_last*100: 0.1f} %')

        st.markdown('###### オリジナル金額(全店)')

        diff = int(now_original_sum - last_original_sum)
        diff2 = '{:,}'.format(diff)
        ratio = f'{now_original_sum / last_original_sum*100:0.1f} %'
        df_original_sum = pd.DataFrame(list([now_original_sum, last_original_sum, ratio, diff]), index=['今期', '前期', '対前年比', '対前年差'])
        df_original_sum2 = pd.DataFrame(list([now_original_sum, last_original_sum]), index=['今期', '前期'], columns=['金額'])
        

        col1, col2 = st.columns(2)
        with col1:
            graph.make_bar(df_original_sum2['金額'], df_original_sum2.index)
        with col2:
            st.metric('対前年比', ratio, delta=diff2)    

        customer_list = df_now['得意先名'].unique()

        index = []
        original_now = []
        original_last = []
        original_rate_now = []
        original_rate_last = []
        original_rate__diff = []

        for customer in customer_list:
            index.append(customer)
            df_now_cust = df_now[df_now['得意先名']==customer]
            df_last_cust = df_last[df_last['得意先名']==customer]
            cust_total_now = df_now_cust['金額'].sum()
            cust_total_last = df_last_cust['金額'].sum()
            original_now_culc = df_now_cust[df_now_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_last_culc = df_last_cust[df_last_cust['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_rate_now_culc = f'{(original_now_culc / cust_total_now)*100: 0.1f} %'
            original_rate_last_culc = f'{(original_last_culc / cust_total_last)*100: 0.1f} %'
            original_rate_diff_culc = f'{((original_now_culc / cust_total_now) - (original_last_culc / cust_total_last))*100: 0.1f} %'
            
            original_now.append(original_now_culc)
            original_last.append(original_last_culc)
            original_rate_now.append(original_rate_now_culc)
            original_rate_last.append(original_rate_last_culc)
            original_rate__diff.append(original_rate_diff_culc)
            
        original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
        st.markdown('###### オリジナル比率(店毎）')   
        st.dataframe(original_rate_list)

    # オリジナル比率（D）
    def original_ratio_d():
        series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
        #ダイニング　全体売上
        sum_now_d = df_now2[df_now2['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        sum_last_d = df_last2[df_last2['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
        #ダイニング　オリジナルdf
        df_now_d = df_now2[df_now2['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        df_last_d = df_last2[df_last2['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
        #ダイニング　オリジナル売上
        now_original_d_sum = df_now_d[df_now_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        last_original_d_sum = df_last_d[df_last_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        #ダイニング　オリジナル比率
        ratio_now_d = f'{now_original_d_sum / sum_now_d*100:0.1f} %'
        ratio_last_d = f'{last_original_d_sum / sum_last_d*100:0.1f} %'
        
        diff_d = f'{((now_original_d_sum / sum_now_d)-(last_original_d_sum / sum_last_d))*100:0.1f} %'

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown('##### オリジナル/ダイニング')
            graph.make_bar_nowlast([now_original_d_sum], [last_original_d_sum], ['金額'])
        with col2:
            st.metric('今期', value=f'{ratio_now_d} ', delta=diff_d)
        with col3:
            st.metric('前期', value=f'{ratio_last_d} ')

        with st.expander('詳細', expanded=False):
            lastyear_ratio = f'{(now_original_d_sum / last_original_d_sum)*100:0.1f} %' 
            st.metric('売上 対前年比', lastyear_ratio) 
        
            st.metric('売上 対前年差', now_original_d_sum - last_original_d_sum) 

        customer_list = df_now['得意先名'].unique()

        index = []
        original_now = []
        original_last = []
        original_rate_now = []
        original_rate_last = []
        original_rate__diff = []

        for customer in customer_list:
            index.append(customer)
            df_now_cust = df_now[df_now['得意先名']==customer]
            df_last_cust = df_last[df_last['得意先名']==customer]
            df_now_cust_d = df_now_cust[df_now_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
            df_last_cust_d = df_last_cust[df_last_cust['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]
            now_cust_d_sum = df_now_cust_d['金額'].sum()
            last_cust_d_sum = df_last_cust_d['金額'].sum()
            original_now_d_culc = df_now_cust_d[df_now_cust_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_last_d_culc = df_last_cust_d[df_last_cust_d['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_rate_now_culc = f'{(original_now_d_culc / now_cust_d_sum)*100: 0.1f} %'
            original_rate_last_culc = f'{(original_last_d_culc / last_cust_d_sum)*100: 0.1f} %'
            original_rate_diff_culc = f'{((original_now_d_culc / now_cust_d_sum) - (original_last_d_culc / last_cust_d_sum))*100: 0.1f} %'
            
            original_now.append(original_now_d_culc)
            original_last.append(original_last_d_culc)
            original_rate_now.append(original_rate_now_culc)
            original_rate_last.append(original_rate_last_culc)
            original_rate__diff.append(original_rate_diff_culc)
            
        original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
        st.markdown('###### オリジナル比率(ダイニング/店毎）')   
        st.dataframe(original_rate_list)

    # オリジナル比率(L)
    def original_ratio_l():
        series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
        #リニング　全体売上
        sum_now_l = df_now2[df_now2['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        sum_last_l = df_last2[df_last2['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
        #リビング　オリジナルdf
        df_now_l = df_now2[df_now2['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        df_last_l = df_last2[df_last2['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
        #リビング　オリジナル売上
        now_original_l_sum = df_now_l[df_now_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        last_original_l_sum = df_last_l[df_last_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
        
        #リビング　オリジナル比率
        ratio_now_l = f'{now_original_l_sum / sum_now_l*100:0.1f} %'
        ratio_last_l = f'{last_original_l_sum / sum_last_l*100:0.1f} %'
        
        diff_l = f'{((now_original_l_sum / sum_now_l) - (last_original_l_sum / sum_last_l))*100:0.1f} %'

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown('##### オリジナル/リビング')
            graph.make_bar_nowlast([now_original_l_sum], [last_original_l_sum], ['金額'])
        with col2:
            st.metric('今期', value=f'{ratio_now_l} ', delta=diff_l)
        with col3:
            st.metric('前期', value=f'{ratio_last_l} ')

        with st.expander('詳細', expanded=False):
            lastyear_ratio = f'{(now_original_l_sum / last_original_l_sum)*100:0.1f} %' 
            st.metric('売上 対前年比', lastyear_ratio) 
        
            st.metric('売上 対前年差', now_original_l_sum - last_original_l_sum) 

        customer_list = df_now['得意先名'].unique()

        index = []
        original_now = []
        original_last = []
        original_rate_now = []
        original_rate_last = []
        original_rate__diff = []

        for customer in customer_list:
            index.append(customer)
            df_now_cust = df_now[df_now['得意先名']==customer]
            df_last_cust = df_last[df_last['得意先名']==customer]
            df_now_cust_l = df_now_cust[df_now_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
            df_last_cust_l = df_last_cust[df_last_cust['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]
            now_cust_l_sum = df_now_cust_l['金額'].sum()
            last_cust_l_sum = df_last_cust_l['金額'].sum()
            original_now_l_culc = df_now_cust_l[df_now_cust_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_last_l_culc = df_last_cust_l[df_last_cust_l['シリーズ名'].isin(['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ'])]['金額'].sum()
            original_rate_now_culc = f'{(original_now_l_culc / now_cust_l_sum)*100: 0.1f} %'
            original_rate_last_culc = f'{(original_last_l_culc / last_cust_l_sum)*100: 0.1f} %'
            original_rate_diff_culc = f'{((original_now_l_culc / now_cust_l_sum) - (original_last_l_culc / last_cust_l_sum))*100: 0.1f} %'
            
            original_now.append(original_now_l_culc)
            original_last.append(original_last_l_culc)
            original_rate_now.append(original_rate_now_culc)
            original_rate_last.append(original_rate_last_culc)
            original_rate__diff.append(original_rate_diff_culc)
            
        original_rate_list = pd.DataFrame(list(zip(original_now, original_last, original_rate_now, original_rate_last, original_rate__diff)), index=index, columns=['今期売上', '前期売上', '今期比率', '前期比率', '対前年差'])
        st.markdown('###### オリジナル比率(リビング/店毎）')   
        st.dataframe(original_rate_list)    

    def original_sum_ld():
        
        series_list = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
        sum_now_d_list = []
        sum_last_d_list = []
        sum_now_l_list = []
        sum_last_l_list = []
        ratio_d_list = []
        ratio_l_list = []
        diff_d_list = []
        diff_l_list = []

        for series in series_list:
            df_now_series = df_now2[df_now2['シリーズ名']==series]
            df_last_series = df_last2[df_last2['シリーズ名']==series]
            sum_now_d = df_now_series[df_now_series['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
            sum_last_d = df_last_series[df_last_series['商品分類名2'].isin(['ダイニングテーブル', 'ダイニングチェア', 'ベンチ'])]['金額'].sum()
            sum_now_l = df_now_series[df_now_series['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
            sum_last_l = df_last_series[df_last_series['商品分類名2'].isin(['クッション', 'リビングチェア', 'リビングテーブル'])]['金額'].sum()
            ratio_d = f'{sum_now_d / sum_last_d*100:0.1f} %'
            ratio_l = f'{sum_now_l / sum_last_l*100:0.1f} %'
            diff_d = sum_now_d - sum_last_d
            diff_l = sum_now_l - sum_last_l
            sum_now_d_list.append(sum_now_d)
            sum_last_d_list.append(sum_last_d)
            sum_now_l_list.append(sum_now_l)
            sum_last_l_list.append(sum_last_l)
            ratio_d_list.append(ratio_d)
            ratio_l_list.append(ratio_l)
            diff_d_list.append(diff_d)
            diff_l_list.append(diff_l)
        
        columns =['今期', '前期', '前年比', '対前年差']
        df_d = pd.DataFrame(list(zip(sum_now_d_list, sum_last_d_list, ratio_d_list, diff_d_list)), index=series_list, columns=columns)   
        df_l = pd.DataFrame(list(zip(sum_now_l_list, sum_last_l_list, ratio_l_list, diff_l_list)), index=series_list, columns=columns)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### オリジナル売上　ダイニング')
            graph.make_bar_nowlast(df_d['今期'], df_d['前期'], df_d.index)

        with col2:
            st.markdown('##### オリジナル売上　リビング')
            graph.make_bar_nowlast(df_l['今期'], df_l['前期'], df_l.index)

        with st.expander('詳細', expanded=False):
            st.markdown('###### dining')
            st.dataframe(df_d)

            st.markdown('###### living')
            st.dataframe(df_l)

    #回転数/分類別/品番別 
    def category_hinban_cnt():

        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            'category:',
            category,
            key='category_hinban_cnt'  
        )
        df_now_cate =df_now2[df_now2['商品分類名2']==option_category]
        df_last_cate =df_last2[df_last2['商品分類名2']==option_category]

        hinban_list = df_now_cate['商品コード2'].unique()

        cnt_list_now = []
        cnt_list_last =[]
        index_list = []
        ratio_list = []
        diff_list = []

        for hinban in hinban_list:
            index_list.append(hinban)
            cnt_now =df_now_cate[df_now_cate['商品コード2']==hinban]['数量'].sum()
            cnt_last = df_last_cate[df_last_cate['商品コード2']==hinban]['数量'].sum()
            ratio = f'{(cnt_now / cnt_last)*100:0.1f} %'
            diff = cnt_now - cnt_last

            cnt_list_now.append(cnt_now)
            cnt_list_last.append(cnt_last)
            ratio_list.append(ratio)
            diff_list.append(diff)

        df_result = pd.DataFrame(index=index_list)
        df_result['今期'] = cnt_list_now
        df_result['前期'] = cnt_list_last
        df_result['対前期比'] = ratio_list
        df_result['対前期差'] = diff_list

        df_result = df_result.sort_values('今期', ascending=False)

        #グラフ
        graph.make_bar_nowlast(df_result['今期'][:10], df_result['前期'][:10], df_result.index)

        with st.expander('詳細', expanded=False):
            st.dataframe(df_result)
    #回転数/シリーズ別/品番別       
    def series_hinban_cnt():
        # *** selectbox シリーズ***
        series = df_now['シリーズ名'].unique()
        option_series = st.selectbox(
            'series:',
            series,   
        )
        df_now_series = df_now2[df_now2['シリーズ名']==option_series]
        df_last_series = df_last2[df_last2['シリーズ名']==option_series]
        
        hinban_list = df_now_series['商品コード2'].unique()
        index = []
        hinban_count_now_list = []
        hinabn_count_last_list = []
        diff = []
        ratio = []

        for hinban in hinban_list:
            index.append(hinban)
            hinabn_count_now = df_now_series[df_now_series['商品コード2']==hinban]['数量'].sum()
            hinabn_count_last = df_last_series[df_last_series['商品コード2']==hinban]['数量'].sum()
            hinban_count_now_list.append(hinabn_count_now)
            hinabn_count_last_list.append(hinabn_count_last)
            diff_culc = hinabn_count_now - hinabn_count_last
            diff.append(diff_culc)
            ratio_culc = f'{(hinabn_count_now / hinabn_count_last)*100:0.1f} %'
            ratio.append(ratio_culc)

        df_result = pd.DataFrame(list(zip(hinban_count_now_list, hinabn_count_last_list, ratio, diff)), \
                                index=index, columns=['今期', '前期', '対前年比', '対前年差'])
        
        df_result = df_result.sort_index(ascending=True)
        #グラフ
        graph.make_bar_nowlast(df_result['今期'], df_result['前期'], df_result.index)
        with st.expander('詳細', expanded=False):
            st.dataframe(df_result) 
        
    #回転数/品番別/得意先別
    def category_hinban_cust_cnt():
        # *** selectbox 商品分類2***
        category = df_now['商品分類名2'].unique()
        option_category = st.selectbox(
            '商品分類:',
            category,   
        )
        df_now_cate =df_now2[df_now2['商品分類名2']==option_category]
        df_last_cate =df_last2[df_last2['商品分類名2']==option_category]

        hinban_list = df_now_cate['商品コード2'].unique()
        option_hinban = st.selectbox(
            '品番:',
            hinban_list,   
        )
        df_now_cate_hin = df_now_cate[df_now_cate['商品コード2']==option_hinban]
        df_last_cate_hin = df_last_cate[df_last_cate['商品コード2']==option_hinban]

        cust_list = df_now_cate_hin['得意先名'].unique()

        cnt_list_now = []
        cnt_list_last =[]
        index_list = []
        diff_list = []
        ratio_list = []

        for cust in cust_list:
            cnt_now = df_now_cate_hin[df_now_cate_hin['得意先名']==cust]['数量'].sum()
            cnt_last = df_last_cate_hin[df_last_cate_hin['得意先名']==cust]['数量'].sum()
            diff = cnt_now - cnt_last
            ratio = f'{(cnt_now / cnt_last)*100:0.1f} %'

            index_list.append(cust)
            cnt_list_now.append(cnt_now)
            cnt_list_last.append(cnt_last)
            diff_list.append(diff)
            ratio_list.append(ratio)

        df_result = pd.DataFrame(index=index_list)
        df_result['今期'] = cnt_list_now
        df_result['前期'] = cnt_list_last
        df_result['対前期比'] = ratio_list
        df_result['対前期差'] = diff_list

        df_result = df_result.sort_values('今期', ascending=False)

        st.dataframe(df_result) 

    # 売上/シリーズ別/品番別
    def hinban_sum():
        # *** selectbox シリーズ***
        series = df_now['シリーズ名'].unique()
        option_series = st.selectbox(
            'series:',
            series,   
        )
        df_now_series = df_now2[df_now2['シリーズ名']==option_series]
        df_last_series = df_last2[df_last2['シリーズ名']==option_series]
        
        hinban_list = df_now_series['商品コード2'].unique()
        index = []
        hinban_sum_now_list = []
        hinabn_sum_last_list = []
        diff = []
        ratio = []

        for hinban in hinban_list:
            index.append(hinban)
            hinabn_sum_now = df_now_series[df_now_series['商品コード2']==hinban]['金額'].sum()
            hinabn_sum_last = df_last_series[df_last_series['商品コード2']==hinban]['金額'].sum()
            hinban_sum_now_list.append(hinabn_sum_now)
            hinabn_sum_last_list.append(hinabn_sum_last)
            diff_culc = hinabn_sum_now - hinabn_sum_last
            diff.append(diff_culc)
            ratio_culc = f'{(hinabn_sum_now / hinabn_sum_last)*100:0.1f} %'
            ratio.append(ratio_culc)

        df_result = pd.DataFrame(list(zip(hinban_sum_now_list, hinabn_sum_last_list, ratio, diff)), \
                                index=index, columns=['今期', '前期', '対前年比', '対前年差'])
        
        df_result = df_result.sort_index(ascending=True)
        graph.make_bar_nowlast(df_result['今期'], df_result['前期'], df_result.index)

        with st.expander('詳細', expanded=False):
            st.dataframe(df_result)

        
    #累計　シリーズベース
    def original_series_category_earnings_sum():
        

        with st.form(key='original_series_category_earnings_sum'):
            # *** selectbox シリーズ***
            series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
            option_series = st.selectbox(
                'series:',
                series,   
            ) 
            # *** selectbox 商品分類2***
            category = df_now['商品分類名2'].unique()
            option_category = st.selectbox(
                'category:',
                category,   
            )
            submitted = st.form_submit_button('submit')

        customer_list = df_now2['得意先名'].unique()
        df_now_series = df_now2[df_now2['シリーズ名']==option_series]
        df_now_series_cate = df_now_series[df_now_series['商品分類名2']==option_category]

        customer_list = df_last2['得意先名'].unique()
        df_last_series = df_last2[df_last2['シリーズ名']==option_series]
        df_last_series_cate = df_last_series[df_last_series['商品分類名2']==option_category]

        sum_now = df_now_series_cate['金額'].sum()
        sum_last = df_last_series_cate['金額'].sum()
        sum_diff = '{:,}'.format(sum_now - sum_last)
        sum_ratio = f'{(sum_now / sum_last)*100:0.1f} %'

        st.markdown('###### オリジナル売上(全店)')
        col1, col2, col3 = st.columns(3)
        with col1:
            df_earn = pd.DataFrame(list([sum_now, sum_last]), index=['今期', '前期'], columns=['金額'])
            graph.make_bar(df_earn['金額'], df_earn.index)
            
        with col2:
            st.metric('今期', value='{:,}'.format(sum_now), delta=sum_diff)
            st.write(sum_ratio)
            
        with col3:
            st.metric('前期', value='{:,}'.format(sum_last))
            
        sum_now = []
        sum_last = []
        sum_ratio = []
        sum_diff = []

        df_result = pd.DataFrame(index=customer_list)

        for customer in customer_list:
            df_now_series_cate_cust = df_now_series_cate[df_now_series_cate['得意先名']==customer]
            df_last_series_cate_cust = df_last_series_cate[df_last_series_cate['得意先名']==customer]
            sum_now_culc = df_now_series_cate_cust['金額'].sum()
            sum_last_culc = df_last_series_cate_cust['金額'].sum()
            sum_ratio_culc = f'{(sum_now_culc/sum_last_culc)*100:0.1f} %'
            sum_diff_culc = sum_now_culc - sum_last_culc

            sum_now.append(sum_now_culc)
            sum_last.append(sum_last_culc)
            sum_ratio.append(sum_ratio_culc)
            sum_diff.append(sum_diff_culc)
        df_result['今期'] = sum_now
        df_result['前期'] = sum_last
        df_result['対前年比'] = sum_ratio
        df_result['対前年差'] = sum_diff
        with st.expander('詳細', expanded=False):
            st.caption('店舗別一覧')
            st.dataframe(df_result)


    #累計　カテゴリーベース
    def original_category_seriesearnings_sum():
        with st.form(key='original_category_seriesearnings_sum'):
            # *** selectbox 商品分類2***
            category = df_now['商品分類名2'].unique()
            option_category = st.selectbox(
                'category:',
                category,   
            )

            # *** selectbox シリーズ***
            series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
            option_series = st.selectbox(
                'series:',
                series,   
            )
            submitted = st.form_submit_button('submit')

        customer_list = df_now2['得意先名'].unique()
        df_now_cate = df_now2[df_now2['商品分類名2']==option_category]
        df_now_cate_seri = df_now_cate[df_now_cate['シリーズ名']==option_series]

        customer_list = df_last2['得意先名'].unique()
        df_last_cate = df_last2[df_last2['商品分類名2']==option_category]
        df_last_cate_seri = df_last_cate[df_last_cate['シリーズ名']==option_series]

        sum_now = df_now_cate_seri['金額'].sum()
        sum_last = df_last_cate_seri['金額'].sum()
        sum_diff = '{:,}'.format(sum_now - sum_last)
        sum_ratio = f'{(sum_now / sum_last)*100:0.1f} %'

        st.markdown('###### オリジナル売上(全店)')
        col1, col2, col3 = st.columns(3)
        with col1:
            df_earn = pd.DataFrame(list([sum_now, sum_last]), index=['今期', '前期'], columns=['金額'])
            st.bar_chart(df_earn, width=200, height=350, use_container_width=False)
            
        with col2:
            st.metric('今期', value='{:,}'.format(sum_now), delta=sum_diff)
            st.write(sum_ratio)
            
        with col3:
            st.metric('前期', value='{:,}'.format(sum_last))
            
        sum_now = []
        sum_last = []
        sum_ratio = []
        sum_diff = []

        df_result = pd.DataFrame(index=customer_list)

        for customer in customer_list:
            df_now_cate_seri_cust = df_now_cate_seri[df_now_cate_seri['得意先名']==customer]
            df_last_cate_seri_cust = df_last_cate_seri[df_last_cate_seri['得意先名']==customer]
            sum_now_culc = df_now_cate_seri_cust['金額'].sum()
            sum_last_culc = df_last_cate_seri_cust['金額'].sum()
            sum_ratio_culc = f'{(sum_now_culc/sum_last_culc)*100:0.1f} %'
            sum_diff_culc = sum_now_culc - sum_last_culc

            sum_now.append(sum_now_culc)
            sum_last.append(sum_last_culc)
            sum_ratio.append(sum_ratio_culc)
            sum_diff.append(sum_diff_culc)
        df_result['今期'] = sum_now
        df_result['前期'] = sum_last
        df_result['対前年比'] = sum_ratio
        df_result['対前年差'] = sum_diff
        st.caption('店舗別一覧')
        st.dataframe(df_result)
        


    #月毎　シリーズベース
    def original_series_category_earnings():
        with st.form(key='original_series_category_earnings'):
            # *** selectbox シリーズ***
            series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
            option_series = st.selectbox(
                'series:',
                series,   
            ) 
            # *** selectbox 商品分類2***
            category = df_now['商品分類名2'].unique()
            option_category = st.selectbox(
                'category:',
                category,   
            )
            submitted = st.form_submit_button('submit')

        customer_list = df_now2['得意先名'].unique()

        df_now_series = df_now2[df_now2['シリーズ名']==option_series]
        df_now_series_cate = df_now_series[df_now_series['商品分類名2']==option_category]
        
        sum_now = []
        df_result = pd.DataFrame(index=customer_list)

        for month in month_list:
            for customer in customer_list:
                df_now_series_cate_cust = df_now_series_cate[df_now_series_cate['得意先名']==customer]
                sum_month = df_now_series_cate_cust[df_now_series_cate_cust['受注年月']==month]['金額'].sum()
                sum_now.append('{:,}'.format(sum_month))
            df_result[month] = sum_now
            sum_now = []
        st.caption('今期売上')
        st.table(df_result)

    # 月毎　カテゴリーベース
    def original_category_series_earnings():
        with st.form(key='original_category_series_earnings'):
            # *** selectbox 商品分類2***
            category = df_now['商品分類名2'].unique()
            option_category = st.selectbox(
                'category:',
                category,   
            )
            # *** selectbox シリーズ***
            series = ['森の記憶', 'LEVITA (ﾚｳﾞｨﾀ)', '悠々', 'とき葉', '青葉', '東京ｲﾝﾃﾘｱｵﾘｼﾞﾅﾙ']
            option_series = st.selectbox(
                'series:',
                series,   
            )
            submitted = st.form_submit_button('submit')
            
        customer_list = df_now2['得意先名'].unique()
        
        df_now_cate = df_now2[df_now2['商品分類名2']==option_category]
        df_now_cate_series = df_now_cate[df_now_cate['シリーズ名']==option_series]
        
        sum_now = []
        df_result = pd.DataFrame(index=customer_list)

        for month in month_list:
            for customer in customer_list:
                df_now_cate_series_cust = df_now_cate_series[df_now_cate_series['得意先名']==customer]
                sum_month = df_now_cate_series_cust[df_now_cate_series_cust['受注年月']==month]['金額'].sum()
                sum_now.append('{:,}'.format(sum_month))
            df_result[month] = sum_now
            sum_now = []
        st.caption('今期売上')
        st.table(df_result)

    def mean_sales():
        st.write('#### 平均成約単価')

        columns_list = ['今期', '前期', '対前年差', '対前年比']

        order_num_now = []
        for num in df_now2['伝票番号']:
            num2 = num.split('-')[0]
            order_num_now.append(num2)
        df_now2['order_num'] = order_num_now

        order_num_last = []
        for num in df_last2['伝票番号']:
            num2 = num.split('-')[0]
            order_num_last.append(num2)
        df_last2['order_num'] = order_num_last

        earnings_now = []
        earnings_last = []
        earnings_diff = []
        earnings_rate = []

        cust_list = df_now2['得意先名'].unique()

        for cust in cust_list:
            df_now_cust = df_now2[df_now2['得意先名']==cust]
            df_last_cust = df_last2[df_last2['得意先名']==cust]

            df_now_cust_order = df_now_cust.groupby('order_num')['金額'].sum()
            df_last_cust_order = df_last_cust.groupby('order_num')['金額'].sum()

            now_cust_order_mean = df_now_cust_order.mean()
            last_cust_order_mean = df_last_cust_order.mean()

            mean_diff = now_cust_order_mean - last_cust_order_mean

            if last_cust_order_mean == 0:
                order_mean_rate = '0%'
            else:
                order_mean_rate = f'{(now_cust_order_mean / last_cust_order_mean)*100: 0.1f} %'

            earnings_now.append(now_cust_order_mean)
            earnings_last.append(last_cust_order_mean)
            earnings_diff.append(mean_diff)
            earnings_rate.append(order_mean_rate)  

        df_mean_earninngs = pd.DataFrame(list(zip(earnings_now, earnings_last, earnings_diff, earnings_rate)),\
                columns=columns_list, index=cust_list)
        st.caption('受注ベース') 

        col1, col2 = st.columns(2)

        with col1:
            st.metric('今期平均', value='{:,}'.format(int(df_mean_earninngs['今期'].mean())), \
                delta='{:,}'.format(int(df_mean_earninngs['対前年差'].mean())))

        with col2:
            st.metric('前期平均', value='{:,}'.format(int(df_mean_earninngs['前期'].mean()))) 

        df_mean_earninngs.fillna(0, inplace=True)
        df_mean_earninngs['今期'] = \
            df_mean_earninngs['今期'].map(lambda x: '{:,}'.format(int(x))) 
        df_mean_earninngs['前期'] = \
            df_mean_earninngs['前期'].map(lambda x: '{:,}'.format(int(x))) 
        df_mean_earninngs['対前年差'] = \
            df_mean_earninngs['対前年差'].map(lambda x: '{:,}'.format(int(x)))   
        
        st.table(df_mean_earninngs)  


    def main():
        # アプリケーション名と対応する関数のマッピング
        apps = {
            '-': none5,
            '店毎売上(トータル/オリジナル)': all_data,
            'オリ比率（全体）●': original_ratio,
            'オリ比率（ダイニング）●': original_ratio_d,
            'オリ比率（リビング）●': original_ratio_l,
            'オリ売上 シリーズ/LD別●': original_sum_ld,
            '回転数/商品分類別/品番別': category_hinban_cnt,
            '回転数/シリーズ別/品番別●': series_hinban_cnt,
            '回転数/品番別/店舗別':category_hinban_cust_cnt,
            '売上/シリーズ別/品番別●': hinban_sum,
            'オリ売上累計 店別/シリーズ/分類●': original_series_category_earnings_sum,
            'オリ売上累計 店別/分類/シリーズ●':original_category_seriesearnings_sum,
            'オリ売上月毎 店別/シリーズ/分類●': original_series_category_earnings,
            'オリ売上月毎 店別/分類/シリーズ●': original_category_series_earnings,
            '平均成約単価/店舗別': mean_sales
            
        }
        selected_app_name = st.selectbox(label='分析項目の選択',
                                                options=list(apps.keys()), key='tab5')
        
        link = '[home](https://cocosan1-hidastreamlit4-linkpage-7tmz81.streamlit.app/)'
        st.sidebar.markdown(link, unsafe_allow_html=True)
        st.sidebar.caption('homeに戻る')  
  

        # 選択されたアプリケーションを処理する関数を呼び出す
        render_func = apps[selected_app_name]
        render_func()

    if __name__ == '__main__':
        main()

