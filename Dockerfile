FROM python:3.12.9-slim

# 設定工作目錄
WORKDIR /app

# [關鍵修正 2] 設定環境變數
# 防止 Python 產生 .pyc 檔 (在容器中不需要)
ENV PYTHONDONTWRITEBYTECODE=1
# 確保 Log 輸出不被緩衝 (讓你能在 Docker logs 立即看到錯誤)
ENV PYTHONUNBUFFERED=1

# 安裝基本系統套件 (保留你的設定，這是對的)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 1. 複製要求清單
COPY requirements.txt .

# 2. 安裝套件
# [關鍵修正 3] 移除矛盾的鏡像源註解，保持乾淨
# 使用 --no-cache-dir 減小映像檔體積
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. 複製其餘程式碼
COPY . .

# 給予腳本執行權限
RUN chmod +x start.sh

# 開放埠口 (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000 8501

# 啟動指令
CMD ["./start.sh"]