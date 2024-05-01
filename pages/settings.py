"""
| streamlit - multipage app - page3_setting |
--------
目標：實作一個供設定查詢天氣資訊所需參數的頁面
--------
紀錄：

"""

### 載入套件
import json
import streamlit as st
from app import authenticator
from streamlit_extras.switch_page_button import switch_page

if st.session_state["logout"]:
    switch_page("首頁")
else:
    name = st.session_state['name']
    ### 大標題
    st.title("設定查詢條件")
    ### 開啟設定檔
    with open("user_setting.json") as f:
        user_settings = json.load(f)
        if name in user_settings:
            pass
        else:
            user_settings[name] =\
                    {
                        "source": None, 
                        "weather": False, 
                        "temperature": False, 
                        "precipitation": False
                    }
    ### 設定 tabs (後面的 tab 可以吃到前面 tab 的 variables)
    tab1, tab2, tab3 = st.tabs(["🔗來源選擇", "🪧呈現資訊", "👁‍🗨設定預覽"])
    with tab1:
        st.header("請選擇獲取天氣資訊的來源網站")
        options = [":blue[**中央氣象局🛰**]", ":blue[**MSN網站💻**]", ":blue[**兩者混合**]☯"]
        with st.form(key="source"):
            source = st.radio(
                label="請擇一",
                options=options,
                index=None if user_settings[name]["source"]==None else options.index(user_settings[name]["source"])
            )
            submitted = st.form_submit_button("確認")
        if submitted:
            st.markdown(f"<span style='color:navy;font-size:18px;font-weight:bold;'>您已選擇來源 : {source}</span>",
                    unsafe_allow_html=True)
            user_settings[name]["source"] = source
    with tab2:
        st.header("請選擇查詢時要呈現的天氣資訊")
        with st.form(key="information"):
            weather = st.toggle(label="天氣",
                                value=user_settings[name]["weather"])
            temperature = st.toggle(label="溫度",
                                value=user_settings[name]["temperature"])
            precipitation = st.toggle(label="降雨機率",
                                value=user_settings[name]["precipitation"])
            # Note : Every form must have a submit button.
            submitted = st.form_submit_button("送出")
        if submitted:
            st.write("weather", weather, "temperature", temperature, "precipitation", precipitation)
            user_settings[name]["weather"] = weather
            user_settings[name]["temperature"] = temperature
            user_settings[name]["precipitation"] = precipitation
    with tab3:
        st.header("您目前選定的天氣資訊相關設定如下")
        st.markdown(f"<span style='color:navy;font-size:18px;font-weight:bold;'>您已選擇來源 : {source}</span>",
                unsafe_allow_html=True)
        info = []
        if user_settings[name]["weather"]:
            info.append("天氣")
        if user_settings[name]["temperature"]:
            info.append("溫度")
        if user_settings[name]["precipitation"]:
            info.append("降雨機率")
        st.markdown(f"<span style='color:navy;font-size:18px;font-weight:bold;'>您已選擇呈現資訊 : :blue[**{'、'.join(info)}**]</span>",
                unsafe_allow_html=True)
        with open('user_setting.json', 'w', encoding='utf8') as json_file:
            json.dump(user_settings, json_file, ensure_ascii=False) # ensure_ascii=False 避免中文出現亂碼 
    # ----- HIDE STREAMLIT STYLE -----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    authenticator.logout("Logout", "sidebar", key='search')
