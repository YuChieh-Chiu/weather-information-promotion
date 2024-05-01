"""
目標：將爬取的天氣資訊存進 MongoDB
--------
| MongoDB 架構 |
連線對象 —— 數據庫 —— 集合（數據表）—— 文檔（記錄）
# 必須要有文檔內容，數據庫才會真正被創建
--------
紀錄：

"""

### 載入套件
# python 連接 mongodb
import pymongo

### 將爬取的天氣資訊存進 db
class save_weather_data:
    def __init__(self) -> None: # 開啟 MongoDB 中的資料表
        # 連線 db
        connection_string = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.1"
        myclient = pymongo.MongoClient(connection_string)
        # 創建/開啟數據庫與數據表
        db_name = "weather"
        sheet_data = "data"
        sheet_log = "log"
        weather_db = myclient[db_name]
        self.weather_sheet = weather_db[sheet_data]
        self.log_sheet = weather_db[sheet_log]
    def save_data(self,
                data: dict) -> None: # 將資料存進數據表
        """
        [ 資料表結構 ]
        | _id(內建ㄉ) | source | weather | max_temp | min_temp | precipitation |
        """
        self.weather_sheet.insert_one(data)
    def save_log(self) -> None:    
        self.log_sheet    
        pass
    def search_data(self,
                search_criteria: dict): # 查詢數據表中的資料
        for row in self.weather_sheet.find(search_criteria):
            print(row)
            print("-----")
    

# ### 執行程式碼
# weather_data = {
#             "weather": "下雨",
#             "max_temp": "26",
#             "min_temp": "22",
#             "precipitation": "69%"
#         }
# weather_data["source"] = "MSN"
# db_conn = save_weather_data()
# db_conn.save_data(data=weather_data)
# db_conn.search_data(search_criteria={})