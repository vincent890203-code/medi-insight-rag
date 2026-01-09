from fastapi import FastAPI

app = FastAPI(title="Medi-Insight RAG Service")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}