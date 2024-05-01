"""
| streamlit - multipage app - page1_chat |
--------
目標：實做一個供聊天的介面
--------
紀錄：
2023.11.20 - 之後可以嘗試只保留動詞、形容詞、名詞再 embedding
2023.11.20 - 完成，但查不準，待確認原因
--------
參考：
https://zhuanlan.zhihu.com/p/46016518
https://python.langchain.com/docs/use_cases/question_answering/
https://python.langchain.com/docs/integrations/vectorstores/chroma
https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L12-v2
https://clusteredbytes.pages.dev/posts/2023/langchain-parent-document-retriever/
vector embeddings : 1. feature engineering 2. neural network
chroma : 專門用來存 embedding 結果的向量資料庫
"""

### 載入套件
import os
import sys
import time
import streamlit as st
from app import authenticator
from streamlit_extras.switch_page_button import switch_page
sys.path.insert(0, "..") # 告訴 python 從父資料夾開始往下找
from dotenv import load_dotenv
from QAflow.parse_data import parse_data
from QAflow.lda_clustering import lda_clustering
from QAflow.build_index import build_index
from QAflow.retrieve_data import retrieve_data

# 載入環境變數
load_dotenv()
indexing_folder = os.getenv("indexing_folder")
# 詞嵌入模型名稱
model_name = os.getenv("model_name")
# chroma 資料夾
chroma_dir = os.getenv("chroma_dir")
# data 資料夾
data_dir = os.getenv("data_dir")
# embeddings 切 chunk 參數
child_chunk_size = int(os.getenv("child_chunk_size"))
child_chunk_overlap = int(os.getenv("child_chunk_overlap"))
# lda 主題數
n_topics = int(os.getenv("n_topics"))

if st.session_state["logout"]:
    switch_page("首頁")
else:
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
    ### 大標題
    st.title("常見氣象問答")
    ### 初始化 messages 共用變數
    if "messages" not in st.session_state:
        st.session_state.messages = []
    ### 保存對話紀錄
    for message in st.session_state.messages:
        with st.chat_message(name=message["role"], avatar=message["avatar"]):
            st.markdown(message["content"], unsafe_allow_html=True)
    ### 對話區（:= 為象牙運算子）
    if prompt := st.chat_input("請輸入問題！"):
        st.session_state.messages.append({"role": "user", "avatar": "👨‍💻", "content": prompt})
        # 使用者提問
        with st.chat_message(name="user", avatar="👨‍💻"):
            st.markdown(prompt)
        # 機器人回答
        with st.chat_message(name="assistant", avatar="🌄"):
            message_placeholder = st.empty()
            time.sleep(0.01)
            ts = time.time()
            with st.spinner("please wait for the answer..."):    
                # 解析資料
                parser = parse_data()
                docs = []
                for filename in os.listdir(indexing_folder):
                    doc = parser.parse_pdf(filepath=f"{indexing_folder}/{filename}")
                    docs.extend(doc)
                # 主題分類
                lda = lda_clustering()
                if (os.path.exists(chroma_dir)) & (os.path.exists(data_dir)):
                    pass
                else:
                    # 訓練分類
                    topics = lda.train(original_docs=docs, n_topics=n_topics)
                    # 建立索引
                    for (topic, all_qa_list) in topics.items():
                        boolean = build_index(topic=topic,
                                            all_qa_list=all_qa_list,
                                            model_name=model_name,
                                            chroma_dir=chroma_dir,
                                            data_dir=data_dir,
                                            child_chunk_size=child_chunk_size,
                                            child_chunk_overlap=child_chunk_overlap)
                # 取得問題分類
                query_topic = lda.predict(query=prompt,
                                        docs=docs,
                                        n_topics=n_topics)
                # 回傳答案
                full_response = retrieve_data(query=prompt,
                                            topic=query_topic,
                                            model_name=model_name,
                                            chroma_dir=chroma_dir,
                                            data_dir=data_dir,
                                            child_chunk_size=child_chunk_size,
                                            child_chunk_overlap=child_chunk_overlap)
                te = time.time()
                elapsed_time = f"<br><span style='font-family:cursive;font-size:14px;color:#6B8E3;'>time spent = {round(te-ts, 2)} seconds.</span>"
                message_placeholder.markdown(full_response + elapsed_time, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "avatar": "🌄", "content": full_response})
