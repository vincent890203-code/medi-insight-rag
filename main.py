# main.py - 這是後端 API (修正來源讀取邏輯)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# 引入路徑維持不變
from app.core.rag import initialize_rag_system 

app = FastAPI(title="Medi-Insight RAG API")

# 全域變數
rag_chain = None

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    global rag_chain
    print("正在初始化 RAG 系統...")
    rag_chain = initialize_rag_system()
    if rag_chain:
        print("✅ RAG 系統初始化完成！")
    else:
        print("⚠️ RAG 系統初始化失敗")

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    global rag_chain
    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG system not ready")
    
    try:
        # 1. 取得回應
        print(f"收到問題: {request.query}") # Debug log
        response = rag_chain.invoke({"input": request.query})
        
        # Debug: 印出 keys 看看 RAG 到底回傳了什麼
        print(f"RAG 回傳 Keys: {response.keys()}")

        # 2. 🔥【關鍵修正】萬能轉接頭 (Universal Adapter)
        # 不管是 context (新版) 還是 source_documents (舊版)，通通抓起來
        source_docs = []
        if "context" in response:
            source_docs = response["context"]
        elif "source_documents" in response:
            source_docs = response["source_documents"]
            
        # 3. 整理來源資料
        sources_list = []
        for doc in source_docs:
            sources_list.append({
                "source": doc.metadata.get("source", "未知來源"),
                "page": doc.metadata.get("page", "未知頁碼"),
                # 🔥【修正點】改回 "content"，確保前端 app.py 看得懂！
                "content": doc.page_content[:150].replace("\n", " ") + "..." 
            })

        print(f"找到 {len(sources_list)} 個參考來源") # Debug log

        return {
            "answer": response["answer"],
            "sources": sources_list
        }

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return {"answer": f"處理發生錯誤: {str(e)}", "sources": []}