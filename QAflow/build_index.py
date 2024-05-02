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

### build index
def build_index(topic,
                all_qa_list: list,
                model_name: str,
                chroma_dir: str,
                data_dir: str,
                child_chunk_size: int,
                child_chunk_overlap: int) -> bool: # 建立索引
    # chroma_dir + topic
    chroma_dir = f"{chroma_dir}/{topic}"
    # data_dir
    data_dir = f"{data_dir}/{topic}"
    # 要用的詞嵌入模型
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    # 將 str 轉 doc
    docs = []
    for _, qa in enumerate(all_qa_list):
        id = f"Q{randint(1, 10000)}"
        doc = {
            id: qa
        }
        doc =  Document(page_content=doc[id], 
                    metadata={"doc_id": id})
        docs.append(doc)
    # 儲存 child chunks
    vectorstore = Chroma.from_documents(documents=docs, 
                                    embedding=embeddings, 
                                    persist_directory=chroma_dir)
    vectorstore.persist()
    # 創建 child splitter
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size,
                                                    chunk_overlap=child_chunk_overlap)
    # 儲存 parent chunks
    fs = LocalFileStore(data_dir)
    store = create_kv_docstore(fs)
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
    )
    retriever.add_documents(docs, ids=None)
    return True
