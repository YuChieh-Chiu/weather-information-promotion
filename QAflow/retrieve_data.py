### import package
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import LocalFileStore # ByteStore
from langchain_community.vectorstores import Chroma
from langchain.storage._lc_store import create_kv_docstore # docstore
from langchain_ollama import ChatOllama  # the latest version solution to deal with `NotImplementedError`
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

### retrieve data
def retrieve_data(query: str,
                topic: str,
                model_name: str,
                chroma_dir: str,
                data_dir: str,
                child_chunk_size: int,
                child_chunk_overlap: int) -> str: # 搜尋相似文件並回傳
    """
    `vectorstores` are used to store embeddings. 
    And as we’re only embedding the smaller chunks 
    (as they capture better semantic meaning after embedding them),
    we use vectorstore to only store the smaller chunks, not the larger ones.
    -----
    For the larger ones tho, we use `InMemoryStore`. 
    It’s like a dictionary type `KEY-VALUE` pair data structure, 
    that stays in the memory while the program is running.
    -----
    In the `InMemoryStore`,
    Each key is a unique uuid for each large chunk
    Each value is the actual text content of the corresponding large chunk
    -----
    In the `vectorstore`,
    For each embedding of the smaller chunks, 
    we store that unique uuid of the parent large chunk as a metadata. 
    This large chunk is from where this small chunk is originated.
    """
    # chroma_dir + topic
    chroma_dir = f"{chroma_dir}/{topic}"
    # data_dir
    data_dir = f"{data_dir}/{topic}"
    # 要用的詞嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"trust_remote_code":True} # prevent model from parameters being initialized
    )
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
    # 回傳 parent document (retrieve)
    retrieved_docs = retriever.invoke(query) 
    document = retrieved_docs[0].page_content
    # 載入 llm (gemma:2b) w/Ollama
    llm = ChatOllama(model="gemma:2b", temperature=0) # 因為是跑在本地端，所以使用小小模型 gemma:2b
    # system prompt (use easy CoT, chain of thought)
    rag_system_prompt = """You are a question-answering expert skilled at answering users' questions based on retrieved documents.
    Please note that if you cannot answer the user's question using the documents, you should directly reply with `查無資訊`.
    Hallucinations will be penalized.
    Please answer in Traditional Chinese and double-check your answer for accuracy.
    Let's think step by step."""
    # prompt 模板
    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", rag_system_prompt),
            ("system", "document:\n```{document}```"),
            ("human", "user question: {question}"),
        ]
    )
    # 建立 RAG 問答鏈 w/LCEL
    rag_chain = rag_prompt | llm | StrOutputParser()
    llm_generation = rag_chain.invoke(
            {
                "question": query,
                "document": document
            }
        )
    return f"<span style='font-size:16px;color:#33488F'>參考資料：<br>{document}<br><br>AI回答：<br>{llm_generation}</span>"
