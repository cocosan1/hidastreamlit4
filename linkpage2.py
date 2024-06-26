import streamlit as st
from PIL import Image
import openpyxl
from io import BytesIO

st.set_page_config(page_title='link_page')
st.markdown('### link page')

col1, col2 = st.columns(2)
with col1:
    img_megane = Image.open('img//電卓アイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### 分析')

    with st.expander('アプリ概要', expanded=False):
        st.write('■ 売上分析')
        st.caption('全体/得意先一覧/得意先個別/エリア/TIF')
        st.caption('今期と前期のデータの期間が同じ')
        st.write('■ 売上分析/前期通年')
        st.caption('全体/得意先一覧/得意先個別/エリア/TIF')
        st.caption('前期のデータは通年')
        st.write('■ 売上分析/品番別傾向')
        st.caption('品番別の傾向分析')
        st.write('■ ハウス催事集計')
        st.caption('催事で入力した見積もりの集計')
        st.write('■ 月次レポート出力')
        st.caption('得意先との打ち合わせ用レポートの自動作成、出力')

    st.link_button('売上分析', 'https://cocosan1-hidastreamlit4-allinone2-jv1drl.streamlit.app/')
    st.link_button('売上分析/前年通年', 'https://cocosan1-hidastreamlit4-allinone-allyear-u99utd.streamlit.app/')
    st.link_button('売上分析/品番別傾向', 'https://hidaapp4-ranking.streamlit.app/')
    st.link_button('ハウス催事集計', 'https://cocosan1-house-main-7e68g1.streamlit.app/')
    st.link_button('月次レポート出力', 'https://cocosan1-hidastreamlit4-report2-i9oc7w.streamlit.app/')

    # link = '[売上分析](https://cocosan1-hidastreamlit4-allinone2-jv1drl.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    # link = '[売上分析/前年通年](https://cocosan1-hidastreamlit4-allinone-allyear-u99utd.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    # link = '[売上分析/品番別傾向](https://hidaapp4-ranking.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    # link = '[ハウス催事集計](https://cocosan1-house-main-7e68g1.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    # link = '[月次レポート出力](https://cocosan1-hidastreamlit4-report2-i9oc7w.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    #目標入力フォームdownload
    st.image('download.png', width=30)
    st.caption('目標入力フォームのダウンロード/月次レポート用')

    # Excelファイルを読み込み、バイナリデータに変換する
    wb = openpyxl.load_workbook(filename='目標入力フォーム.xlsx')
    stream = BytesIO()
    wb.save(stream)
    data = stream.getvalue()

    with st.expander('目標入力フォーム注意事項', expanded=False):
        st.write('● 得意先名は【受注委託移動在庫生産照会】のデータからコピー')
        st.write('● 目標数値部分は数値のみ入力 ※カンマ不要')

    # ダウンロードボタンを表示する
    st.download_button(label='ダウンロード開始', data=data, file_name=f'目標入力フォーム.xlsx')

with col2:
    img_megane = Image.open('img//電卓アイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### 分析(詳細)')

    with st.expander('アプリ概要', expanded=False):
        st.write('■ 売上分析')
        st.caption('全体/得意先一覧/得意先個別/エリア/TIF')


    st.link_button('売上分析', 'https://cocosan1-hidastreamlit4-allinone2-jv1drl.streamlit.app/')
    





    img_megane = Image.open('img//電卓アイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### その他')

    with st.expander('アプリ概要', expanded=False):
        st.write('■ 納期カレンダー作成')
        st.caption('納期カレンダーの自動計算')
        st.write('■ 廃番品の特定、見積')
        st.caption('廃番品の特定から見積まで')
        st.write('■ 市況状況/全国')
        st.caption('市況情報の取得　※情報は常に最新/着工数は市単位での検索可')
        st.write('■ PDF結合/ハウス')
        st.caption('ハウス　御見積書と明細書の結合/ファイル名はお客様名_見積NOにて作成')
        st.write('■ ソファ画像の検索')
        st.caption('ソファの画像を塗色や張地などを指定して検索')
        st.write('■ 売り場画像の検索')
        st.caption('売り場の画像を壁紙、床、シリーズなどを指定して検索')

    st.link_button('納期カレンダー作成', 'https://hidacalender3-calender.streamlit.app/')
    st.link_button('廃番品の特定、見積', 'https://repairapp-main.streamlit.app/')
    st.link_button('市況状況/全国', 'https://cocosan1-market-condition-main-zenkoku-l78svj.streamlit.app/')
    st.link_button('PDF結合/ハウス', 'https://cocosan1-pdf-connect-connect-slgprv.streamlit.app/')
    st.link_button('ソファ画像の検索', 'https://sofasimulator-app.streamlit.app/')
    st.link_button('売り場画像の検索', 'https://uribadb-app.streamlit.app/')
