# check_models.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 載入環境變數
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ 錯誤：找不到 GOOGLE_API_KEY，請檢查 .env 檔案")
    exit()

# 2. 設定 API
genai.configure(api_key=api_key)

print("🔍 正在查詢您的 API Key 可用模型列表...")
print("------------------------------------------------")

try:
    # 3. 直接向 Google 請求列表
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 可用模型 ID: {m.name}")
            available_models.append(m.name)
            
    print("------------------------------------------------")
    if not available_models:
        print("⚠️  警告：您的 API Key 連線成功，但沒有權限存取任何對話模型。")
        print("👉 可能原因：API Key 尚未開通 Generative AI 服務，或區域受限。")
    else:
        print(f"💡 請複製上面其中一個 'models/xxx' 到你的 rag.py 裡面替換。")

except Exception as e:
    print(f"❌ 連線致命錯誤: {e}")