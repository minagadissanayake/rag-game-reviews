from fastapi import APIRouter
from pydantic import BaseModel
from app.retrieval.retriever import retrieve
from openai import OpenAI
from app.config import settings

router = APIRouter()
client = OpenAI(api_key=settings.openai_api_key)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    hits = retrieve(req.question)
    context = "\n\n".join([h["text"] for h in hits])

    prompt = f"""You are a knowledgeable game critic assistant.
Answer the user's question using only the game information provided below.
Be specific — mention game names, scores, and genres where relevant.
If the answer isn't in the context, say "I don't have enough information about that."
Always mention which games you're drawing from in your answer.

Game data:
{context}

User question: {req.question}
"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}]
    )

    return QueryResponse(
        answer=response.choices[0].message.content,
        sources=hits
    )