FROM python:3.11-slim

WORKDIR /app

# 安裝基本系統套件
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 1. 複製要求清單
COPY requirements.txt .

# 2. 終極安裝指令 (解決 Timeout 與 版本錯亂)
# --default-timeout=1000: 解決 image_098b7c.png 的超時問題
# -i https://pypi.tuna.tsinghua.edu.tw/simple: 使用鏡像站加速，避免跨海連線不穩
# --no-cache-dir: 確保不讀取 image_14f087.png 提到的錯誤快取
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 \
    -i https://pypi.org/simple \
    --no-cache-dir \
    -r requirements.txt

# 3. 複製其餘程式碼
COPY . .

EXPOSE 8000 8501

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]