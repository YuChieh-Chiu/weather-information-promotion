### reference
# https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# https://stackoverflow.com/questions/77438251/langchain-parentdocumetretriever-save-and-load

### import package
import re
import pdfplumber

### parse data
class parse_data:
    def __init__(self) -> None:
        pass
    def fullmatch_pattern(self,
                        patterns:list, 
                        line:str) -> bool: # 判斷讀進來的 line 是否 fullmatch 列表中的 pattern
        for pattern in patterns:
            if re.fullmatch(pattern, line):
                return True
            else:
                pass
        return False
    def parse_pdf(self, 
                filepath: str) -> list: # 解析 pdf
        # 要排除的 line 或 pattern
        except_lines = [
            "::: 回⾸⾴ EN 網站導覽 意⾒箱 常⾒問答 關於氣象署 ⼩ 中 ⼤   ",
            "警特報 天氣 ⽣活 地震 海象 氣候 資料 知識與天⽂ 常⽤服務",
            " ⾼溫資訊",
            "  知識與天⽂  氣象百科  氣候百問  什麼是氣候全書下載",
            " 什麼是氣候全書下載",
            "::: 導覽 | 科普網 | 常⾒問答 | 雙語詞彙 | RSS服務 | 意⾒箱 | 好站介紹 | 會員登入 | 退休資訊專區 | 勤休新制專區 | 隱私權保護政策 | 資訊安全政策 | 政府網站資料開放宣告 | 個⼈資料保護專區",
            "諮詢服務：08:30⾄17:30 資料申購：08:30⾄17:00 地址：100006臺北市中正區公園路64號",
            "|",
            "總機：(02)2349-1000(代表號) 氣象查詢：(02)2349-1234 地震查詢：(02)2349-1168",
            "中華⺠國交通部中央氣象署 版權所有 轉載請註明出處 本網站參考時間：臺灣標準時間TST(GMT +08:00)"
        ]
        ocr_lines = [
            "昨天宜商下雨了",
            "⼀曰下兩"
        ]
        except_pattern = [
            r"什麼是氣候全書下載 \| 交通部中央氣象署 2023/11/5 下午[1-9]{1}:[0-9]{2}",
            r"https://www.cwa.gov.tw/V8/C/K/Encyclopedia/climate/.{1,}.html 第[0-9]{1,}⾴（共[0-9]{1,}⾴）",
            r"圖[0-9]{1,}-[0-9]{1,}.*"
        ]
        sub_pattern = [
            r"https://www.cwa.gov.tw/V8/C/K/Encyclopedia/climate/.{1,}.html 第[0-9]{1,}⾴（共[0-9]{1,}⾴）",
            r"\([如]{0,1}圖[0-9]{1,}-[0-9]{1,}\)"
        ]
        # 裝檔案中的所有 QA
        qa_list = []
        with pdfplumber.open(filepath) as pdf:
            qa = ""
            for page in pdf.pages:
                content = page.extract_text()
                lines = content.split("\n")
                for line in lines:
                    if (line in except_lines) | (line in ocr_lines) | (self.fullmatch_pattern(except_pattern, line)):
                        pass
                    else:
                        for pattern in sub_pattern:
                            line = re.sub(pattern, "", line)
                        start_line = r"^[0-9]{1,3}\..*?$" # QA 開始列 : 問句
                        if (re.fullmatch(start_line, line) != None) & (qa != ""):
                            qa_list.append(qa) # 將原本的 qa 放入 qa list
                            qa = line # 開始收集新的 qa
                        else:
                            qa += line
        return qa_list