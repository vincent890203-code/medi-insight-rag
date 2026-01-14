import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 設定環境
load_dotenv()

# 設定資料路徑
# 為了配合 web_ui.py 在根目錄執行，這裡的路徑相對於專案根目錄
DATA_PATH = "data/" 
DB_PATH = "faiss_index"

def create_vector_db():
    """
    讀取 PDF 並建立 FAISS 向量資料庫。
    回傳值: (success: bool, message: str)
    """
    log_messages = [] # 用來收集執行過程的訊息
    
    log_messages.append(f"📂 檢查資料來源路徑: {DATA_PATH} ...")
    
    # 檢查路徑是否存在
    if not os.path.exists(DATA_PATH):
        error_msg = f"❌ 錯誤：找不到路徑 {DATA_PATH}"
        print(error_msg)
        return False, error_msg

    # 2. 智慧載入
    documents = []
    
    try:
        if os.path.isfile(DATA_PATH):
            # 單一檔案模式
            loader = PyPDFLoader(DATA_PATH)
            documents.extend(loader.load())
            log_messages.append(f"  - 載入單一檔案: {DATA_PATH}")
            
        elif os.path.isdir(DATA_PATH):
            # 資料夾模式 (掃描所有 PDF)
            log_messages.append(f"  - 掃描資料夾中...")
            pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]
            
            if not pdf_files:
                return False, "⚠️ 資料夾內沒有 PDF 檔案，請先確認 data/ 目錄。"
                
            for file in pdf_files:
                pdf_path = os.path.join(DATA_PATH, file)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
                log_messages.append(f"  - 載入: {file}")
    except Exception as e:
        return False, f"❌ 讀取 PDF 失敗: {str(e)}"
    
    if not documents:
        return False, "⚠️ 沒讀到任何內容，請檢查 PDF 是否加密或空白。"

    log_messages.append(f"✅ PDF 讀取成功，共 {len(documents)} 頁")

    # 3. 切割文字
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    log_messages.append(f"🔪 文字切割完成：共產生 {len(docs)} 個片段 (Chunks)")

    # 4. 轉成向量
    log_messages.append("🧠 正在載入 Embedding 模型 (all-MiniLM-L6-v2)...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except Exception as e:
        return False, f"❌ Embedding 模型載入失敗: {str(e)}"

    # 5. 建立並儲存資料庫 (FAISS)
    log_messages.append(f"💾 正在建立向量索引並存檔至 {DB_PATH}...")
    try:
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(DB_PATH)
    except Exception as e:
        return False, f"❌ FAISS 儲存失敗: {str(e)}"

    final_msg = "\n".join(log_messages)
    print(final_msg) # 保留終端機輸出方便除錯
    return True, final_msg

if __name__ == "__main__":
    # 如果直接執行此腳本，只印出結果
    success, msg = create_vector_db()
    if not success:
        sys.exit(1)