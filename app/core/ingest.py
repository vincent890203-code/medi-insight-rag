import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS # <--- 關鍵改變：我們用 FAISS

# 1. 設定環境
load_dotenv()

# 設定資料路徑
# 為了讓你稍後不用改來改去，我寫了防呆：
# 如果 data 是資料夾，它會讀資料夾；如果是檔案，它讀檔案。
DATA_PATH = "data/patient_report_001.pdf" 
DB_PATH = "faiss_index"

def create_vector_db():
    print(f"📄 正在準備讀取: {DATA_PATH} ...")
    
    # 檢查路徑是否存在
    if not os.path.exists(DATA_PATH):
        print(f"❌ 錯誤：找不到路徑 {DATA_PATH}")
        return

    # 2. 智慧載入 (修正原本的 Bug)
    documents = []
    if os.path.isfile(DATA_PATH):
        # 如果是單一檔案 (你的情況)
        loader = PyPDFLoader(DATA_PATH)
        documents.extend(loader.load())
    elif os.path.isdir(DATA_PATH):
        # 如果是資料夾 (未來的擴充性)
        for file in os.listdir(DATA_PATH):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(DATA_PATH, file)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
    
    if not documents:
        print("⚠️ 沒讀到任何內容，程式結束。")
        return

    print(f"✅ 成功載入，共 {len(documents)} 頁")

    # 3. 切割文字
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    print(f"🔪 已切割成 {len(docs)} 個片段")

    # 4. 轉成向量
    print("🧠 正在載入 Embedding 模型 (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. 建立並儲存資料庫 (FAISS)
    print("💾 正在建立向量索引並存檔...")
    # 注意：這裡用 FAISS.from_documents，不是 Chroma
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(DB_PATH)
    print(f"✅ 成功！FAISS 向量資料庫已儲存至: {DB_PATH}")

if __name__ == "__main__":
    create_vector_db()