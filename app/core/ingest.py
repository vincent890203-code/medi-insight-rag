# app/core/ingest.py

import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# ❌ 移除 Google
# ✅ 改用 HuggingFace 本地模型
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma

load_dotenv()

DATA_PATH = "data/"
DB_PATH = "chroma_db"

def ingest_documents():
    print(f"🔄 [Local Embedding 版] 準備開始...")

    # 1. 清理舊資料庫
    if os.path.exists(DB_PATH):
        print("🧹 清理舊資料庫...")
        shutil.rmtree(DB_PATH)
    
    # 2. 讀取 PDF
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(DATA_PATH, file)
            print(f"📖 讀取檔案: {file}")
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

    if not documents:
        print("⚠️ 無檔案，結束。")
        return

    # 3. 切分文字
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  共切分為 {len(chunks)} 個區塊。")

    # 4. 初始化本地模型 (關鍵步驟)
    print("🧠 正在載入 HuggingFace 本地模型 (首次執行會下載模型，約 100MB)...")
    
    # 使用標準的輕量級模型
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 5. 快速入庫 (因為是本地端，不用 sleep，可以直接衝)
    print("🚀 開始高速向量化 (Local Compute)...")
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )

    print(f"🎉 成功！所有資料已存入 {DB_PATH}")
    print("💡 提示：因為使用本地模型，以後查詢都不需要 Embedding 的 API Key 了！")

if __name__ == "__main__":
    ingest_documents()