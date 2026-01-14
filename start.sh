#!/bin/bash

# 1. 啟動後端 (關鍵修改：拿掉 nohup 和 log redirection，讓 Log 直接吐到螢幕)
# 這樣你在 docker run 的視窗就能看到 "Application startup complete"
echo "🚀 Starting Backend (FastAPI)..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 2. 等待機制 (稍微加長一點，確保 Transformer 模型載入完畢)
echo "⏳ Waiting for RAG Model to load (10s)..."
sleep 10

# 3. 啟動前端 (這是主程序，不能背景執行)
echo "✨ Starting Frontend (Streamlit)..."
streamlit run web_ui.py --server.port 8501 --server.address 0.0.0.0