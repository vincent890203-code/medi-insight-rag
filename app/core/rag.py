import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document

load_dotenv()

def start_chat():
    print("🧠 正在啟動 Medi-Insight RAG 系統 (本地穩定版)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 建立範例知識庫
    docs = [Document(page_content="病人張三，EGFR L858R 突變陽性，建議使用 Osimertinib。")]
    vector_store = FAISS.from_documents(docs, embeddings)
    retriever = vector_store.as_retriever()

    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0)
    prompt = ChatPromptTemplate.from_template("根據內容回答：{context}\n問題：{input}")

    # 核心處理鏈
    qa_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)

    print("✅ 系統就緒！")
    while True:
        user_input = input("\n👨‍⚕️ 醫師提問: ")
        if user_input.lower() in ['q', 'exit']: break
        res = rag_chain.invoke({"input": user_input})
        print(f"\n📝 AI 診斷：{res['answer']}")

if __name__ == "__main__":
    start_chat()