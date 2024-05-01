"""
【總目標】
透過 streamlit 建立查詢天氣的網頁，並透過 render 部署服務（部署部分再看看）
--------
參考：
https://tw.piliapp.com/emoji/list/weather/ [--emoji--]
https://hackmd.io/@davidho9713/streamlit_data_visualization_basic
https://medium.com/starbugs/render-來試試用來取代-heroku-的服務吧-render-的網路服務部署介紹-b728e86d5716
--------
紀錄：
2023.10.14：基本上 streamlit 的概念很簡單，程式碼的上下順序就是網頁呈現的上下順序。
2023.10.15：透過 switch_page 額外模組解決 streamlit 登入登出頁面跳轉問題。
2023.10.17：透過 st_pages 額外套件解決 streamlit 檔名與 sidebar 標題顯示對應的問題。
========

| streamlit - multipage app - login page |
--------
目標：實作一個輸入帳密登入的頁面
--------
參考：
https://www.redhat.com/zh/topics/automation/what-is-yaml
https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
https://medium.com/@HUSAM_007/streamlit-authentication-bf6385a71e78
https://www.hwchiu.com/docs/2023/python-yaml
https://github.com/bharath5673/streamlit-multipage-authentication/tree/main [--前人作品--]
--------
紀錄：
config.yaml 跟 app.py 要在同一層，其他頁都應該放在 /pages 底下。
"""

### 載入套件
import time
from datetime import datetime
from ruamel.yaml import YAML # load/dump yaml with comments
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page # 頁面跳轉
from st_pages import Page, show_pages, hide_pages # 處理頁名

# 設定要被顯示在 sidebar 的頁面們與頁面樣態
show_pages(
    [
        Page("app.py", "首頁", "🏠"),
        Page("pages/chat.py", "聊天", "📱"),
        Page("pages/search.py", "查詢", "🔎"),
        Page("pages/settings.py", "設定", "⚙️"),
    ]
)

### hash 密碼
# hashed_passwords = stauth.Hasher(["jackloginweather!!"]).generate()
# hashed_passwords

### 載入儲存使用者驗證資訊的 yaml 檔案
yaml = YAML()
with open("config.yaml", "r") as file:
    config = yaml.load(file)

### 創建使用者驗證 object
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

### 隱藏 sidebar
hide_bar = """
        <style>
                section[data-testid="stSidebar"][aria-expanded="true"]{
                    display: none;
                }
        </style>
        """

### 大標題
if st.session_state["authentication_status"] != True:
    st.title("天氣資訊推播平台")

### 登入頁面（參數 = 標題、位置[可選 sidebar / main]）
authenticator.login("Login", "main")

### 使用者驗證 part
if st.session_state["authentication_status"]: # 成功登入
    st.title("首頁")
    # ----- HIDE STREAMLIT STYLE -----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    authenticator.logout("Logout", "sidebar", key='homepage')
    # 首頁內容 - 歡迎詞
    hour = datetime.now().hour
    if 4 <= hour < 11:
        greet = "早安"
        greet_icon = "🌅"
    elif 11 <= hour <= 17:
        greet = "午安"
        greet_icon = "🌇"
    else:
        greet = "晚安"
        greet_icon = "🌃"
    welcome_text =\
        f"""
        <h3>嗨 <span style='color:#33488F'>{st.session_state['name']}</span> {greet}{greet_icon}, 歡迎使用天氣資訊推播網站!</h3>
        """
    st.markdown(welcome_text, unsafe_allow_html=True)
    st.divider() # 劃一條線
    # 首頁內容 - 操作提示
    first_time = True
    for acc, user in config["credentials"]["usernames"].items():
        if user["name"] == st.session_state['name']:
            acc = acc
            first_time = user["first_time"]
            break
    if first_time:
        # 先隱藏其他分頁(分頁2~4)
        display = ""
        for idx in range(1,4):
            display += f"""
                    div[data-testid=\"stSidebarNav\"] li:nth-child({idx + 1}) {{
                        display: none;
                    }}
                """
        display =\
            f"""
            <style>
                {display}
            </style>
            """
        st.write(display, unsafe_allow_html=True)
        # 提示詞
        hint_text = "<h4 style='color:#8B0000'>請先閱讀以下網站指引後，再開始使用網站</h4>"
        st.markdown(hint_text, unsafe_allow_html=True)
        # 進度條
        t = 0
        progress_bar = st.progress(t, text=f"網站指引閱讀進度（{t}/3）")
        with st.expander(label=":blue[設定]", expanded=False):
            st.text("您可以透過此頁面設定您在查詢天氣資訊時，天氣的資料來源以及要顯示的天氣資訊。")
            setting_check = st.checkbox("閱讀完畢", key="setting")
            if setting_check:
                t = t+34 if t//33==2 else t+33
                progress_bar.progress(t, text=f"網站指引閱讀進度（{t//33}/3）")
        with st.expander(label=":blue[查詢]", expanded=False):
            st.warning("在使用查詢頁面查詢特定行政區的天氣資訊前，請先確保您已完成設定頁面的設定。")
            st.text("確認設定完成後，您即可透過此頁面查詢特定行政區明日的天氣。")
            search_check = st.checkbox("閱讀完畢", key="search")
            if search_check:
                t = t+34 if t//33==2 else t+33
                progress_bar.progress(t, text=f"網站指引閱讀進度（{t//33}/3）")
        with st.expander(label=":blue[聊天]", expanded=False):
            st.info("本系統天氣資訊知識庫出自 [`中央氣象局`] 知識問答。")
            st.text("您可以使用此頁面，詢問系統常見的天氣知識問題。")
            chat_check = st.checkbox("閱讀完畢", key="chat")
            if chat_check:
                t = t+34 if t//33==2 else t+33
                progress_bar.progress(t, text=f"網站指引閱讀進度（{t//33}/3）")
        if t == 100:
            st.success("恭喜閱讀完網站指引 🎉 祝您使用愉快~")
            # 確實閱讀完後，將使用者是否為初次登入的變數改為否
            config["credentials"]["usernames"][acc]["first_time"] = False
            with open("config.yaml", "w") as file:
                yaml.dump(
                    config,
                    file
                )
            # 再展開其他分頁(分頁2~4)
            display = ""
            for idx in range(1,4):
                display += f"""
                        div[data-testid=\"stSidebarNav\"] li:nth-child({idx + 1}) {{
                            display: block;
                        }}
                    """
            display =\
                f"""
                <style>
                    {display}
                </style>
                """
            st.write(display, unsafe_allow_html=True)
    else:
        st.info("歡迎使用本網站，如需再次閱讀網站指引，請點擊下方按鈕 ⛏")
        hint_btn = st.button(label=":violet[再次閱讀網站指引]", key="hint")
        if hint_btn: # 更改 first_time 值，更新頁面顯示網站指引
            with st.spinner("處理中，請稍候..."):
                config["credentials"]["usernames"][acc]["first_time"] = True
                with open("config.yaml", "w") as file:
                    yaml.dump(
                        config,
                        file
                    )
                st.rerun()
elif st.session_state["authentication_status"] == False: # 登入失敗
    st.error("Username/Password 不正確，請重新輸入。")
    st.markdown(hide_bar, unsafe_allow_html=True)
elif st.session_state["authentication_status"] == None: # 預設文字
    st.warning("請輸入你的 Username 與 Password。")
    st.markdown(hide_bar, unsafe_allow_html=True)
else:
    pass

