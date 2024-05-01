"""
| streamlit - multipage app - page2_search |
--------
目標：實作一個供查詢天氣資訊的頁面
--------
紀錄：

"""

### 載入套件
import re
import json
import streamlit as st
from app import authenticator
from crawler import get_weather_from_web
from storage import save_weather_data
from datetime import datetime, timedelta
from streamlit_extras.switch_page_button import switch_page

if st.session_state["logout"]:
    switch_page("首頁")
else:
    ### 大標題
    st.title("天氣資訊查詢")
    name = st.session_state['name']
    city_town = st.selectbox(
        label=":gray[🇹🇼選擇行政區]",
        options=("臺北市松山區", "臺北市信義區", "臺北市大安區", "臺北市中山區", "臺北市中正區",
                "臺北市大同區", "臺北市萬華區", "臺北市文山區", "臺北市南港區", "臺北市內湖區",
                "臺北市士林區", "臺北市北投區"),
        placeholder="請輸入或點選要查找的行政區（請輸入正體字）",
        index=None
    )
    if city_town is None:
        pass
    else:
        tomorrow = datetime.now() + timedelta(1)
        tomorrow = tomorrow.strftime("%Y/%m/%d")
        st.markdown(f"<br>您選擇的行政區為：<span style='color:navy;font-weight:bold'>{city_town}</span>，明日（{tomorrow}）天氣資訊如下。",
                unsafe_allow_html=True)
        # crawl -> store -> show weather data
        ### 開啟設定檔
        with open("user_setting.json") as f:
            user_settings = json.load(f)
            if name in user_settings:
                # crawler
                with st.spinner(text="氣象資訊獲取中..."):
                    city_pattern = r'.{2}市'
                    town_pattern = r'.{2}區'
                    city = re.search(city_pattern, city_town).group()
                    town = re.search(town_pattern, city_town).group()
                    search_criteria = json.dumps({
                        "town": town,
                        "city": city
                    })
                    crawler = get_weather_from_web()
                    source = user_settings[name]["source"]
                    if source == ":blue[**中央氣象局🛰**]":
                        weather_forecast = crawler.get_cwa_weather(search_criteria=search_criteria)
                    elif source == ":blue[**MSN網站💻**]":
                        weather_forecast = crawler.get_msn_weather(search_criteria=search_criteria)
                    else: # 兩者混合 = 取平均
                        cwa = crawler.get_cwa_weather(search_criteria=search_criteria)
                        msn = crawler.get_msn_weather(search_criteria=search_criteria)
                        weather = f"<br>中央氣象局 : {cwa['weather']}<br>MSN : {msn['weather']}"
                        min_temp = int((int(cwa['min_temp'][:-1]) + int(msn['min_temp'][:-1]))/2)
                        max_temp = int((int(cwa['max_temp'][:-1]) + int(msn['max_temp'][:-1]))/2)
                        precipitation = (float(cwa['precipitation'][:-1]) + float(msn['precipitation'][:-1])) / 2
                        weather_forecast = {
                            "weather": weather,
                            "min_temp": f"{min_temp}°",
                            "max_temp": f"{max_temp}°",
                            "precipitation": f"{precipitation}%"
                        }
                # storage
                with st.spinner(text="天氣資訊已爬取完畢，存進 DB 中..."):
                    weather_forecast["source"] = source
                    db_conn = save_weather_data()
                    db_conn.save_data(data=weather_forecast)
                # show
                col1, col2 = st.columns(spec=[1, 1], gap='large')
                with col1:
                    text = weather_forecast["weather"]
                    if ("雲" in text) & ("晴" not in text) & ("雨" not in text):
                        file = "cloudy.png"
                    elif ("陰" in text) & ("晴" not in text) & ("雨" not in text):
                        file = "cloudy.png"
                    elif ("雲" in text) & ("晴" in text) & ("雨" not in text):
                        file = "sunny-2.png"
                    elif ("晴" in text) & ("雲" not in text) & ("雨" not in text):
                        file = "sunny.png"
                    elif ("雨" in text) & ("雷" not in text):
                        file = "heavy-rain.png"
                    elif ("雷" in text):
                        file = "thunder.png"
                    else:
                        file = "weather-forecast.png"
                    st.image(f"天氣圖示/{file}", use_column_width='always')
                with col2:
                    st.header(city_town)
                    # show or not
                    weather_display = "" if user_settings[name]["weather"] else "display:none;"
                    temperature_display = "" if user_settings[name]["temperature"] else "display:none;"
                    precipitation_display = "" if user_settings[name]["precipitation"] else "display:none;"
                    weather_info =\
                        f"""
                        <br>
                        <ul style='font-weight:bold;color:navy;'>
                            <li style='font-size:24px;{weather_display}'>📡 天氣：{weather_forecast['weather']}</li>
                            <li style='font-size:24px;{temperature_display}'>🌡 溫度：{weather_forecast['min_temp']}C ~ {weather_forecast['max_temp']}C</li>
                            <li style='font-size:24px;{precipitation_display}'>💧 降雨機率：{weather_forecast['precipitation']}</li>
                        </ul>
                        """
                    st.markdown(weather_info, unsafe_allow_html=True)
            else:
                st.warning("您尚未設定查詢相關條件，請先至⚙️設定頁面完成相關設定", icon="⚠️")
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
