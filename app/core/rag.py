import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document

# 1. 載入環境變數
load_dotenv()

def initialize_rag_system():
    print("🧠 正在啟動 Medi-Insight RAG 系統 (本地穩定版)...")

    # 2. 準備 Embeddings (全域變數)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
  # 3. 載入向量資料庫 (關鍵修改！)
    DB_PATH = "faiss_index" # 資料庫路徑
    
    if os.path.exists(DB_PATH):
        print(f"📂 發現本地資料庫，正在載入: {DB_PATH}")
        # allow_dangerous_deserialization=True 是必須的
        # 因為 FAISS 讀取 pickle 檔有安全風險，但這是我們自己生成的檔，所以安全
        vector_store = FAISS.load_local(
            DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("⚠️ 警告：找不到 faiss_index 資料夾！")
        print("💡 請先執行 'python app/core/ingest.py' 來消化 PDF。")
        # 萬一真的沒檔案，給個空殼避免程式崩潰
        return None

    # 4. 建立檢索器 (Retriever)
    retriever = vector_store.as_retriever()

    # 5. 設定 LLM (使用我們確認過可用的模型)
    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0)

    # 6. 設定 Prompt Template
    prompt = ChatPromptTemplate.from_template("""
    你是一位專業的醫療 AI 助理。請根據底下的【病歷摘要】來回答醫師的問題。
    如果不確定或資料不在摘要中，請回答「病歷中未提及」。

    【病歷摘要】：
    {context}

    問題：{input}
    """)

    # 核心處理鏈
    qa_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)

    print("✅ RAG核心系統就緒！")

    # 【關鍵修改】必須把做好的鍊傳出去，網頁才拿得到
    return rag_chain

# --- 這是給終端機測試用的函式 ---
def start_terminal_chat():
    # 在這裡呼叫初始化函式
    rag_chain = initialize_rag_system()

    print("🚀 啟動終端機對話模式...")    
    while True:
        try:
            user_input = input("\n👨‍⚕️ 醫師提問(輸入 q 離開): ")
            if user_input.lower() in ['q', 'exit']: 
                print("再見!")
                break
        
            res = rag_chain.invoke({"input": user_input})
            print(f"\n📝 AI 診斷：{res['answer']}")
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")


# --- 程式進入點保護 ---
# 只有直接執行這個檔案時，才會跑終端機對話
# 如果是被 web_ui.py 匯入 (import)，這段不會跑，避免卡死網頁
if __name__ == "__main__":
    start_terminal_chat()