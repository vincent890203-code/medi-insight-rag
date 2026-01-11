import sys
print("Python Executable:", sys.executable)

try:
    print("1. 測試導入 langchain...")
    import langchain
    print(f"   ✅ langchain 版本: {langchain.__version__}")

    print("2. 測試導入 chains...")
    # 這是你報錯的那一行
    from langchain.chains.combine_documents import create_stuff_documents_chain
    print("   ✅ 成功導入 create_stuff_documents_chain")

    print("3. 測試導入 retrieval chain...")
    from langchain.chains import create_retrieval_chain
    print("   ✅ 成功導入 create_retrieval_chain")

except ImportError as e:
    print(f"❌ 導入失敗: {e}")
except Exception as e:
    print(f"❌ 發生其他錯誤: {e}")