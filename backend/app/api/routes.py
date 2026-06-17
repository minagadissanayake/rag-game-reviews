from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from app.config import settings

router = APIRouter()
client = OpenAI(api_key=settings.openai_api_key)

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class QueryRequest(BaseModel):
    question: str
    history: list[Message] = []

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        from app.retrieval.retriever import retrieve
        hits = retrieve(req.question)
    except Exception:
        hits = []

    context = "\n\n".join([h["text"] for h in hits]) if hits else "No game data available."

    system_prompt = f"""You are a game recommendation assistant for GameVaultAI.

CRITICAL RULE: You may ONLY recommend games that are explicitly listed in the game data below.
Do NOT mention any game that does not appear in the provided data, even if you know about it.
If you want to recommend a game, it MUST have a corresponding entry in the data below.
Stick strictly to the provided data. Never use outside knowledge for game recommendations.

For each game you recommend, include its name, rating, Metacritic score, and a brief description from the data.

Game data:
{context}"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": req.question})

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages
    )

    return QueryResponse(
        answer=response.choices[0].message.content,
        sources=hits
    )