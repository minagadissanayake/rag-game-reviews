from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG Game Reviews API", version="1.0.0")
app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}