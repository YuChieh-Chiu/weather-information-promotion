### 載入套件
# 處理時間
import time
from datetime import datetime, timedelta
# 處理資料格式
import json
import pandas as pd
# 處理數值
import numpy as np
# 動態爬蟲
from selenium import webdriver
from selenium.webdriver.common.by import By
# 靜態爬蟲
import requests
from bs4 import BeautifulSoup

### 爬取天氣資訊（以天氣、溫度跟降雨機率為主）
class get_weather_from_web:
    def __init__(self) -> None: # 開啟瀏覽器
        tomorrow = datetime.now() + timedelta(1)
        self.tomorrow = tomorrow.strftime("%Y/%m/%d")
        print(f"明天日期：{self.tomorrow}")
    def get_msn_weather(self, 
                        search_criteria: json) -> dict: # 取得微軟天氣資訊（Selenium）
        search_criteria = json.loads(search_criteria) # json 形式的 str 轉 dict
        town = search_criteria["town"]
        city = search_criteria["city"]
        msn_url = f"https://www.msn.com/zh-tw/weather/forecast/in-{town},{city}"
        safari_options = webdriver.SafariOptions()
        safari_options.add_argument("--headless=new")
        driver = webdriver.Safari(options=safari_options)
        driver.get(msn_url)
        time.sleep(1) # 等待頁面跑完
        # 點選明天的天氣圖卡
        card = driver.find_element(By.XPATH,
                '//*[@id="ForecastDays"]/div/ul/li[2]/button/span')
        card.click()
        time.sleep(1) # 等待點選跑完
        # 取得天氣
        weather = card.find_element(By.CLASS_NAME, 
                "iconTempPartIcon-DS-EntryPoint1-1").get_attribute("title")
        # 取得最高溫
        max_temp = card.find_element(By.CLASS_NAME,
                "topTemp-DS-EntryPoint1-1.temp-DS-EntryPoint1-1.tempSelected-DS-EntryPoint1-1").text
        # 取得最低溫
        min_temp = card.find_element(By.XPATH,
                '//*[@id="ForecastDays"]/div/ul/li[2]/button/span/div/div/div[2]/div[2]/div[1]').text
        # 取得降雨機率
        precipitation = card.find_element(By.CLASS_NAME,
                "precipitationV3-DS-EntryPoint1-1").text
        print(f"""明天天氣：{weather},
明天最高溫：{max_temp},
明天最低溫：{min_temp},
明天降雨機率：{precipitation}""")
        msn_forecast = {
            "weather": weather,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "precipitation": precipitation
        }
        return msn_forecast
    def get_cwa_weather(self,
                        search_criteria: json) -> dict: # 取得中央氣象局天氣資訊（BeautifulSoup）
        # 縣市鄉鎮與 ID 對照
        name2id = {
            "臺北市":{
                "松山區": "6300100",
                "信義區": "6300200",
                "大安區": "6300300",
                "中山區": "6300400",
                "中正區": "6300500",
                "大同區": "6300600",
                "萬華區": "6300700",
                "文山區": "6300800",
                "南港區": "6300900",
                "內湖區": "6301000",
                "士林區": "6301100",
                "北投區": "6301200",
            }
        }
        search_criteria = json.loads(search_criteria) # json 形式的 str 轉 dict
        town = search_criteria["town"]
        city = search_criteria["city"]
        cwa_url = f"https://www.cwa.gov.tw/V8/C/W/Town/MOD/Week/{name2id[city][town]}_Week_PC.html"
        res = requests.get(cwa_url)
        soup = BeautifulSoup(res.text, "html.parser")
        # 比對日期
        for i in range(1,8):
            date = soup.find("th", {"id": f"PC7_D{i}"}).getText()
            if self.tomorrow[5:] in date:
                ti = i
                break
        day_ti = f"PC7_D{ti} PC7_D{ti}D"
        night_ti = f"PC7_D{ti} PC7_D{ti}N"
        # 白天天氣
        day_weather = soup.find("td", {"headers": f"PC7_Wx {day_ti}"})
        day_weather = day_weather.find("img")["title"]
        # 夜晚天氣
        night_weather = soup.find("td", {"headers": f"PC7_Wx {night_ti}"})
        night_weather = night_weather.find("img")["title"]
        # 白天最高溫
        day_max_temp = soup.find("td", {"headers": f"PC7_MaxT {day_ti}"})
        day_max_temp = day_max_temp.find("span", {"class":"tem-C is-active"}).getText()
        # 夜晚最高溫
        night_max_temp = soup.find("td", {"headers": f"PC7_MaxT {night_ti}"})
        night_max_temp = night_max_temp.find("span", {"class":"tem-C is-active"}).getText()
        # 白天最低溫
        day_min_temp = soup.find("td", {"headers": f"PC7_MinT {day_ti}"})
        day_min_temp = day_min_temp.find("span", {"class":"tem-C is-active"}).getText()
        # 夜晚最低溫
        night_min_temp = soup.find("td", {"headers": f"PC7_MinT {day_ti}"})
        night_min_temp = night_min_temp.find("span", {"class":"tem-C is-active"}).getText()
        # 白天降雨機率
        day_precipitation = soup.find("td", {"headers": f"PC7_Po {day_ti}"}).getText()[:-1] # 不要％
        # 夜晚降雨機率
        night_precipitation = soup.find("td", {"headers": f"PC7_Po {night_ti}"}).getText()[:-1] # 不要％
        # 取最高溫
        max_temp = f"{max(day_max_temp, night_max_temp)}{chr(176)}"
        # 取最低溫
        min_temp = f"{min(day_min_temp, night_min_temp)}{chr(176)}"
        # 取降雨機率平均
        precipitation = f"{np.mean([int(day_precipitation), int(night_precipitation)])}%"
        print(f"""明天天氣：白天 - {day_weather} | 晚上 - {night_weather},
明天最高溫：{max_temp},
明天最低溫：{min_temp},
明天降雨機率：{precipitation}""")
        cwa_forecast = {
            "weather": f"白天 - {day_weather} | 晚上 - {night_weather}",
            "max_temp": max_temp,
            "min_temp": min_temp,
            "precipitation": precipitation
        }
        return cwa_forecast
