import subprocess
import time
import sys
import os
import signal

# 定義要執行的指令
# 注意：在地端我們用 127.0.0.1 比較安全，也不需要 nohup
backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
frontend_cmd = [sys.executable, "-m", "streamlit", "run", "web_ui.py", "--server.port", "8501"]

def run_services():
    print("🚀 正在啟動 Medi-Insight RAG 系統...")
    
    # 1. 啟動後端 (Backend)
    print("🔥 啟動後端 API (FastAPI)...")
    backend_process = subprocess.Popen(backend_cmd)
    
    # 等待幾秒確保後端已經起來 (避免前端連不到)
    time.sleep(3)
    
    # 2. 啟動前端 (Frontend)
    print("✨ 啟動前端 UI (Streamlit)...")
    frontend_process = subprocess.Popen(frontend_cmd)

    print("\n✅ 系統已啟動！請打開瀏覽器訪問: http://localhost:8501")
    print("⚠️  按 Ctrl+C 可同時關閉所有服務\n")

    try:
        # 讓主程式停在這裡等待，直到使用者按 Ctrl+C
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 偵測到關閉指令，正在清理程序...")
        
        # 優雅關閉 (Terminate)
        frontend_process.terminate()
        backend_process.terminate()
        
        # 確保真的關掉了
        frontend_process.wait()
        backend_process.wait()
        
        print("👋 服務已安全關閉，Port 8000 與 8501 已釋放。")

if __name__ == "__main__":
    run_services()