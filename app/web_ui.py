import streamlit as st
import os
import sys

# 設定路徑，讓 Python 找得到 app.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 從我們剛剛改好的 rag.py 匯入「初始化函式」
from app.core.rag import initialize_rag_system

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Medi-Insight AI", page_icon="🩺", layout="centered")
st.title("🩺 Medi-Insight 智慧病歷助手")
st.caption("🚀 Powered by Gemini Flash & FAISS | Local RAG System")

# --- 2. 核心加速機制 (Caching) ---
# 這個裝飾器告訴 Streamlit：
# 「只要 initialize_rag_system 跑過一次，就把結果存起來，下次不要重跑！」
@st.cache_resource
def get_cached_chain():
    return initialize_rag_system()

# 獲取系統 (第一次會慢，第二次開始秒開)
try:
    with st.spinner("正在啟動 AI 核心引擎，請稍候..."):
        rag_chain = get_cached_chain()
    st.success("✅ 系統已就緒，請開始提問！")
except Exception as e:
    st.error(f"❌ 系統啟動失敗：{str(e)}")
    st.stop()

# --- 3. 初始化對話紀錄 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. 顯示歷史訊息 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. 處理使用者輸入 ---
if prompt := st.chat_input("請輸入關於病人的問題... (例如：張三的診斷結果？)"):
    # 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. 呼叫 AI
    with st.chat_message("assistant"):
        with st.spinner("AI 正在翻閱病歷..."):
            try:
                # invoke 的時候，rag_chain 會回傳 answer 和 context
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]
                
                # 1. 顯示回答
                st.markdown(answer)
                
                # 2. 顯示來源證據 (加分題！)
                # 從 response["context"] 裡抓出它看了哪些文件
                context_docs = response["context"]
                
                # 用一個漂亮的折疊區塊顯示來源
                with st.expander("🔍 點擊查看 AI 參考的病歷片段"):
                    for i, doc in enumerate(context_docs):
                        source_page = doc.metadata.get("page", "未知") + 1 # 頁碼通常從 0 開始，所以 +1
                        source_file = os.path.basename(doc.metadata.get("source", "未知檔案"))
                        
                        st.markdown(f"**📄 來源 {i+1} (第 {source_page} 頁 - {source_file}):**")
                        st.caption(doc.page_content[:200] + "...") # 只顯示前 200 字預覽
                        st.divider()

                # 記錄 AI 的話到歷史訊息
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"❌ 發生錯誤：{str(e)}")