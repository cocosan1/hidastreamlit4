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
        # st.write('■ 売上分析売上分析/データ読み込み自動版')
        # st.caption('データが自動更新されています/毎日18:30')
        st.caption('全体/得意先一覧/得意先個別/エリア/TIF')
        st.write('■ 売上分析/品番別傾向')
        st.caption('品番別の傾向分析')
        st.write('■ 月次レポート出力')
        st.caption('得意先との打ち合わせ用レポートの自動作成、出力')

    link = '[売上分析](https://cocosan1-hidastreamlit3-allinone2-z8cark.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    # link = '[売上分析/★データ読み込み自動版](https://cocosan1-hidastreamlit3-allinone-auto-w7vi90.streamlit.app/)'
    # st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/品番別傾向](https://cocosan1-hidastreamlit3-ranking-mwfyaf.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[月次レポート出力](https://cocosan1-hidastreamlit3-report2-np3t5d.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

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
    st.markdown('###### その他')

    with st.expander('アプリ概要', expanded=False):
        st.write('■ 納期カレンダー作成')
        st.caption('納期カレンダーの自動計算')
        st.write('■ 廃番品の特定、見積')
        st.caption('廃番品の特定から見積まで')
        st.write('■ 市況状況/全国')
        st.caption('市況情報の取得　※情報は常に最新/着工数は市単位での検索可')

    link = '[納期カレンダー作成](https://cocosan1-hidacalender2-calender-m3rc3o.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[廃番品の特定、見積](https://cocosan1-repair-app-main-8jf8bl.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[市況状況/全国](https://cocosan1-market-condition-main-zenkoku-l78svj.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)