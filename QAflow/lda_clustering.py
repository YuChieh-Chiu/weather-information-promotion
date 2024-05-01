### reference
# https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# https://stackoverflow.com/questions/77438251/langchain-parentdocumetretriever-save-and-load

### import package
import re
import os
import pickle
import jieba
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

### lda clustering
class lda_clustering:
    def __init__(self) -> None:
        self.tfidf_vectorizer_path = "model/tf_idf_vectorizer.pickle"
        self.lda_model_path = "model/lda_model.pickle"
    # train lda
    def train(self,
            original_docs: list,
            n_topics: int) -> dict:
        # 初始化 tf-idf vectorizer
        tf_idf_vectorizer = TfidfVectorizer()
        ### docs 資料清理    
        # 去除無意義字詞
        pattern = u'[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!\t"@#$%^&*\\-_=+，。\n《》、？：；“”‘’｛｝【】（）…￥！—┄－]+'
        # 去重複、去缺失、分詞
        stop_words_set = set(["你", "我"]) # 停用詞合集
        docs = (
            pd.Series(original_docs)
            .apply(lambda x: str(x))
            .apply(lambda x: re.sub(pattern, " ", x))
            .apply(lambda x: " ".join([word for word in jieba.lcut(x) if word not in stop_words_set]))
        )
        ### model process
        # 構建 tf-idf
        tf_idf = tf_idf_vectorizer.fit_transform(docs)
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            max_iter=50,
            learning_method='online',
            learning_offset=50,
            random_state=0)
        # 使用 tf_idf 語料訓練 lda
        lda.fit(tf_idf)
        # 將 tf_idf 轉為數組，以便後面使用它來對文本主題概率分佈進行計算
        X:np.ndarray = tf_idf.toarray()
        # 計算完畢主題概率分佈狀況
        matrix = lda.transform(X)
        columns = [f'topic {i+1}' for i in range(len(lda.components_))]
        predict_df = pd.DataFrame(matrix, columns=columns)
        # 整理各主題底下有哪些文章
        topics = {}
        doc_topic = predict_df.idxmax(axis=1) # 取每列最大值
        for idx, topic in enumerate(doc_topic):
            if topic in topics:
                topics[topic] += [original_docs[idx]]
            else:
                topics[topic] = [original_docs[idx]]
        # 將 tfidfvectorizer & lda 模型存起來
        with open(self.tfidf_vectorizer_path, "wb") as v:
            pickle.dump(tf_idf_vectorizer, v)
        with open(self.lda_model_path, 'wb') as f:
            pickle.dump(lda, f)
        return topics
    # predict title of query
    def predict(self,
                query: str,
                docs: list,
                n_topics: int) -> str:
        try:
            with open(self.tfidf_vectorizer_path, "rb") as v:
                tf_idf_vectorizer: TfidfVectorizer = pickle.load(v)
            with open(self.lda_model_path, 'rb') as f:
                lda: LatentDirichletAllocation = pickle.load(f)
        except FileNotFoundError: # 檔案不存在
            _, _ = self.train(original_docs=docs, n_topics=n_topics)                
            with open(self.tfidf_vectorizer_path, "rb") as v:
                tf_idf_vectorizer: TfidfVectorizer = pickle.load(v)
            with open(self.lda_model_path, 'rb') as f:
                lda: LatentDirichletAllocation = pickle.load(f)
        except Exception as e:
            print(f"Error occurred : {e.__class__.__name__}.")
        query_array = tf_idf_vectorizer.transform([query]).toarray()
        query_matrix = lda.transform(query_array)
        columns = [f'topic {i+1}' for i in range(len(lda.components_))]
        query_predict_df = pd.DataFrame(query_matrix, columns=columns)
        query_topic = query_predict_df.idxmax(axis=1)[0] # 取每列的最大值
        return query_topic

    