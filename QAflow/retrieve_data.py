### import package
import os
from random import randint
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import LocalFileStore # ByteStore
from langchain.vectorstores import Chroma
from langchain.storage._lc_store import create_kv_docstore # docstore

### retrieve data
def retrieve_data(query: str,
                topic: str,
                model_name: str,
                chroma_dir: str,
                data_dir: str,
                child_chunk_size: int,
                child_chunk_overlap: int) -> str: # 搜尋相似文件並回傳
    # chroma_dir + topic
    chroma_dir = f"{chroma_dir}/{topic}"
    # data_dir
    data_dir = f"{data_dir}/{topic}"
    # 要用的詞嵌入模型
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    # 載入存好的 child chunks
    vectorstore = Chroma(persist_directory=chroma_dir,
                        embedding_function=embeddings)
    # 創建 child splitter
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size,
                                                    chunk_overlap=child_chunk_overlap)
    # 儲存 parent chunks
    fs = LocalFileStore(data_dir)
    store = create_kv_docstore(fs)
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter
    )
    # 回傳 parent document
    retrieved_docs = retriever.get_relevant_documents(query)
    return f"<span style='font-size:16px;color:#33488F'>{retrieved_docs[0].page_content}</span>"
