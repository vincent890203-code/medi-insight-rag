import os
import sys
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 強制修正路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.rag import get_rag_chain
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

app = FastAPI(title="Medi-Insight RAG API")

class QueryRequest(BaseModel):
    query: str
    file_name: str = None

# --- ✨ 升級版：關鍵句萃取與高亮 (Key Sentence Extraction) ---
def extract_key_context(text: str, query: str) -> str:
    """
    只回傳包含關鍵字的句子，並加上高亮。
    如果完全沒對到關鍵字(純語意相關)，則回傳前 200 字作為摘要。
    """
    # 1. 取得關鍵字 (忽略太短的字)
    keywords = [kw for kw in query.split() if len(kw) > 1]
    
    # 2. 簡單斷句 (針對英文句點、問號或換行切分)
    # 這裡的邏輯是：遇到 . ? ! 或 換行 就切開
    sentences = re.split(r'(?<=[.!?])\s+|\n', text)
    
    # 清理空白
    sentences = [s.strip() for s in sentences if s.strip()]

    selected_sentences = []
    found_match = False

    for sent in sentences:
        # 檢查這句話有沒有包含任何一個關鍵字 (Case Insensitive)
        if any(k.lower() in sent.lower() for k in keywords):
            found_match = True
            
            # 進行高亮處理
            highlighted_sent = sent
            for kw in keywords:
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                highlighted_sent = pattern.sub(lambda m: f"**{m.group(0)}**", highlighted_sent)
            
            selected_sentences.append(highlighted_sent)

    # 3. 組合結果
    if found_match:
        # 如果有找到關鍵句，用 " ... " 連接，讓閱讀感像摘要
        return " ... ".join(selected_sentences)
    else:
        # --- 防呆機制 ---
        # 如果 RAG 找到了段落(因為語意相似)，但沒有精確關鍵字
        # 我們回傳前 2 句就好，不要整坨丟出來
        fallback = " ".join(sentences[:2])
        return f"{fallback} ..."

@app.on_event("startup")
async def startup_event():
    print("🚀 API 啟動中，正在預載入 RAG 模型...")
    get_rag_chain() 

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        print(f"📩 收到提問: {request.query}")

        target_source = None
        if request.file_name:
            target_source = os.path.join("data", request.file_name)
            target_source = target_source.replace("\\", "/")

        rag_chain = get_rag_chain(selected_source=target_source)
        
        if not rag_chain:
            raise HTTPException(status_code=503, detail="RAG init failed.")

        response = rag_chain.invoke({"input": request.query})
        
        sources_list = []
        if "context" in response:
            for doc in response["context"]:
                # 取得原始文字
                raw_content = doc.page_content
                
                # --- 關鍵修改：呼叫新的萃取邏輯 ---
                # 我們不再無腦 replace \n，因為 \n 在病歷中通常代表一個新的項目
                refined_content = extract_key_context(raw_content, request.query)

                sources_list.append({
                    "source": os.path.basename(doc.metadata.get("source", "Unknown")),
                    "page": doc.metadata.get("page", 0) + 1,
                    "content": refined_content 
                })

        return {
            "answer": response["answer"],
            "sources": sources_list
        }

    except Exception as e:
        print(f"❌ 處理錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)