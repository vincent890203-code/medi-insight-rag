import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# 1. 載入環境變數
load_dotenv()

# 全域變數 (Singleton Pattern)
vector_store = None
llm = None
embeddings = None

def initialize_rag_components():
    """初始化核心組件 (只執行一次)"""
    global vector_store, llm, embeddings
    
    if vector_store is not None:
        return # 已經初始化過，直接跳過

    print("正在初始化 Medi-Insight RAG 組件 ...")
    
    # 準備 Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 載入向量資料庫
    DB_PATH = "faiss_index"
    if os.path.exists(DB_PATH):
        print(f"📂 載入本地資料庫: {DB_PATH}")
        vector_store = FAISS.load_local(
            DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("⚠️ 警告：找不到 faiss_index 資料夾！請先執行 ingest。")
        return

    # 設定 LLM
    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0)
    print("✅ RAG 組件初始化完成！")

def get_rag_chain(selected_source=None):
    """
    動態建立 RAG Chain
    :param selected_source: 完整檔案路徑 (例如 'data/patient_report_002.pdf')
    """
    # 確保組件已初始化
    if vector_store is None:
        initialize_rag_components()
        if vector_store is None: return None # 真的沒救了

    # 1. 設定檢索器 (Retriever) 與過濾器
    search_kwargs = {"k": 3}
    
    if selected_source:
        # 💡 關鍵：Metadata Filtering
        # 告訴 FAISS 只搜尋 source 欄位等於 selected_source 的向量
        search_kwargs["filter"] = {"source": selected_source}
        print(f"🔍 [RAG] 啟用過濾模式: 只搜尋 {selected_source}")
    else:
        print("🔍 [RAG] 全域搜尋模式 (搜尋所有病歷)")

    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)

    # 2. 設定 Prompt
    prompt = ChatPromptTemplate.from_template("""
    你是一位專業的醫療 AI 助理。請根據底下的【病歷摘要】來回答醫師的問題。
    注意：你只能回答與該病歷相關的資訊。
    如果不確定或資料不在摘要中，請回答「病歷中未提及」。

    【病歷摘要】：
    {context}

    問題：{input}
    """)

    # 3. 組合 Chain
    qa_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)
    
    return rag_chain