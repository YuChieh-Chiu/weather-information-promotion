### 載入套件
# python 連接 mongodb
import pymongo

### 將爬取的天氣資訊存進 db
class save_weather_data:
    def __init__(self) -> None: # 開啟 MongoDB 中的資料表
        # 連線 db
        connection_string = ""
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
        | _id(內建) | source | weather | max_temp | min_temp | precipitation |
        """
        self.weather_sheet.insert_one(data)
    def search_data(self,
                search_criteria: dict): # 查詢數據表中的資料
        for row in self.weather_sheet.find(search_criteria):
            print(row)
            print("-----")
