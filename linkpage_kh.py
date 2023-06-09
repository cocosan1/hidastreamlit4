import streamlit as st
from PIL import Image

st.set_page_config(page_title='link_page_kh')
st.markdown('#### link page 星川')

col1, col2, col3 = st.columns(3)

with col1:
    img_megane = Image.open('img//電卓アイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### 分析/星川')

    link = '[本日の受注](https://cocosan1-hida-gcp-today-ofag3x.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/全体](https://cocosan1-hidastreamlit-kh-sales-kh2-hj7n9o.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/得意先別](https://cocosan1-hidastreamlit-kh-sales-cust-kh-x9a9mf.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/得意先（個別）](https://cocosan1-hidastreamlit-kh-customer2-owoyjs.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/年齢層](https://cocosan1-hidastreamlit-kh-age-3wf4ye.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/エリア](https://cocosan1-hidastreamlit-kh-area-kh-hiqyx6.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[売上分析/TIF東北](https://cocosan1-hidastreamlit-kh-tif-tohoku-dz7bgt.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)


with col2:
    img_megane = Image.open('img//電卓アイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### 第２世代')
    link = '[展示分析&レコメンド](https://cocosan1-recommend-series2-main-7r9cjj.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[分析2](https://cocosan1-recommend-series2-calc-jbt3a7.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[アソシエーション](https://cocosan1-association-fullhinban-cmy4cf.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[得意先分析2](https://recommend-series2-cust.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)
    

with col3:
    img_megane = Image.open('img/虫眼鏡のアイコン.jpg')
    st.image(img_megane, width=50)
    st.markdown('###### その他')

    link = '[市況情報/南東北](https://cocosan1-market-condition-main-lxvbyd.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[shop/来店者管理](https://cocosan1-kurax-py-gs-linkpage-rxa5f5.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[shop/売上予測](https://shoppred-calkweek.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[Q＆A](https://chatgptnotion-main.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    
    




    





    