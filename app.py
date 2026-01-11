import streamlit as st
import requests
import json

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Medi-Insight 智慧病歷助手",
    page_icon="🩺",
    layout="centered"
)

st.title("✅ Medi-Insight 智慧病歷助手 (v2.3)")
st.caption("🚀 Powered by Gemini 2.0 & RAG Technology")

# --- 2. 初始化聊天紀錄 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. 顯示歷史對話 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 如果歷史訊息裡有來源，也要顯示出來
        if "sources" in message:
            with st.expander("📚 參考來源 (History)"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**{idx+1}. {src.get('source', 'unknown')} (Page {src.get('page', '?')})**")
                    st.caption(src.get('content', ''))

# --- 4. 處理使用者輸入 ---
if prompt := st.chat_input("請輸入關於病歷的問題 (例如: 患者的 EGFR 突變情況如何？)"):
    
    # 4.1 顯示使用者輸入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4.2 呼叫後端 API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        sources_data = [] # 準備接球
        
        try:
            api_url = "http://localhost:8000/chat" 
            
            with st.spinner("AI 正在翻閱病歷資料..."):
                response = requests.post(
                    api_url, 
                    json={"query": prompt}, 
                    timeout=600 
                )
            
            if response.status_code == 200:
                data = response.json()
                full_response = data.get("answer", "⚠️ API 沒有回傳內容")
                # 🔥【關鍵修正】這裡終於要把 sources 接回來了！
                sources_data = data.get("sources", [])
            else:
                full_response = f"⚠️ 伺服器錯誤 (Status: {response.status_code})\n\n錯誤詳情: {response.text}"
                
        except requests.exceptions.ConnectionError:
            full_response = "❌ 無法連線到後端 API。請確認 Uvicorn 是否正在執行？"
        except Exception as e:
            full_response = f"❌ 發生未預期的錯誤: {str(e)}"

        # 4.3 顯示 AI 回答
        message_placeholder.markdown(full_response)
        
        # 🔥【關鍵修正】把接到的 sources 畫出來！
        if sources_data:
            with st.expander("📚 查看參考來源 (References)"):
                for idx, src in enumerate(sources_data):
                    st.markdown(f"**{idx+1}. {src.get('source', 'unknown')} (Page {src.get('page', '?')})**")
                    st.caption(src.get('content', ''))
                    st.divider()

    # 4.4 將 AI 回答加入紀錄 (連同來源一起存)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response,
        "sources": sources_data
    })