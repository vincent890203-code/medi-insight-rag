import streamlit as st
import requests
import os
import sys

# --- 1. 全局配置 & CSS ---
st.set_page_config(
    page_title="Medi-Insight Pro | Clinical Workspace",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .patient-banner {
        background-color: #ffffff;
        border-left: 6px solid #2980B9;
        padding: 15px 20px;
        margin-bottom: 20px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .patient-name { font-size: 1.4rem; font-weight: 700; color: #2C3E50; }
    .file-tag { 
        background-color: #E8F6F3; color: #16A085; 
        padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;
        margin-left: 10px;
    }
    [data-testid="stChatMessage"] { background-color: #f9f9f9; border: 1px solid #eaeded; border-radius: 8px; }
    [data-testid="stChatMessage"][data-testid="user"] { background-color: #EBF5FB; border-left: 4px solid #3498DB; }
    [data-testid="stChatMessage"][data-testid="assistant"] { background-color: #FDFEFE; border-left: 4px solid #2ECC71; }
</style>
""", unsafe_allow_html=True)

# --- 2. 動態讀取 data 資料夾 ---
DATA_FOLDER = "data"

def get_pdf_files():
    """掃描 data 資料夾下的所有 PDF"""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return []
    files = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith(".pdf")]
    files.sort()
    return files

pdf_files = get_pdf_files()

# --- 3. 側邊欄：檔案選擇 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=50)
    st.markdown("### Medi-Insight **Workspace**")
    st.markdown("---")
    
    st.markdown("#### 📂 選擇病歷檔案 (Data Source)")
    
    if pdf_files:
        selected_file = st.selectbox("選擇 PDF", pdf_files, index=0)
        st.info(f"📄 目前掛載: `{selected_file}`")
    else:
        selected_file = None
        st.warning("⚠️ data/ 資料夾中沒有 PDF 檔案")
        st.caption("請先執行 create_pdf.py 生成檔案")

    # Ingest 功能
    if st.button("🔄 重建索引 (Ingest)"):
        with st.spinner("正在讀取 data/ 資料夾並更新向量庫..."):
            try:
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from app.core.ingest import create_vector_db
                success, log = create_vector_db()
                if success:
                    st.success("索引更新成功！")
                    with st.expander("執行細節"):
                        st.text(log)
                else:
                    st.error("更新失敗")
                    st.text(log)
            except ImportError:
                st.error("找不到 app.core.ingest 模組，請確認路徑。")
            except Exception as e:
                st.error(f"執行錯誤: {e}")

    st.markdown("---")
    if st.button("🗑️ 清除對話紀錄"):
        st.session_state.messages = []
        st.rerun()

# --- 4. 主畫面 ---
if selected_file:
    patient_id = "Unknown"
    if "patient_report_" in selected_file:
        patient_id = selected_file.replace("patient_report_", "").replace(".pdf", "")

    st.markdown(f"""
    <div class="patient-banner">
        <span class="patient-name">病歷檔案檢視</span>
        <span class="file-tag">ID: {patient_id}</span>
        <span class="file-tag">File: {selected_file}</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("👈 請從左側選擇一個病歷檔案開始")

# --- 5. 對話邏輯 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    avatar = "👨‍⚕️" if role == "user" else "🧬"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.status("📚 參考文獻", state="complete"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**[{idx+1}] {src.get('source')}** (p.{src.get('page')})")
                    st.caption(src.get('content'))

if prompt := st.chat_input("請輸入關於此病歷的問題..."):
    if not selected_file:
        st.error("請先選擇一個 PDF 檔案")
    else:
        # User
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(prompt)

        # Assistant
        with st.chat_message("assistant", avatar="🧬"):
            message_placeholder = st.empty()
            try:
                with st.spinner("🔍 RAG 檢索分析中..."):
                    backend_host = os.getenv("API_URL", "http://localhost:8000")
                    api_url = f"{backend_host}/chat"
                    
                    # ✅ 關鍵：將 file_name 傳給後端
                    payload = {
                        "query": prompt, 
                        "file_name": selected_file 
                    }
                    
                    response = requests.post(api_url, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        data = response.json()
                        full_response = data.get("answer", "")
                        sources_data = data.get("sources", [])
                        
                        message_placeholder.markdown(full_response)
                        
                        if sources_data:
                            with st.status("✅ 佐證資料 (Evidence)"):
                                for idx, src in enumerate(sources_data):
                                    st.info(f"**{src['source']}** (Page {src['page']})\n\n{src['content']}")
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": full_response,
                            "sources": sources_data
                        })
                    else:
                        err_msg = f"⚠️ 後端錯誤 ({response.status_code}): {response.text}"
                        message_placeholder.error(err_msg)
            
            except requests.exceptions.ConnectionError:
                message_placeholder.error("❌ 無法連線至後端 API (localhost:8000)。請確認是否已執行 `python main.py`。")