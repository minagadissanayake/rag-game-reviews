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
You MUST only recommend games that appear in the game data provided below.
Do not recommend any games from your own knowledge that are not in the provided data.
If the data doesn't contain enough relevant games, say so honestly rather than inventing recommendations.
Be specific — mention game names, scores, and genres from the data.
For follow-up questions, use the conversation history to maintain context.

Game data for current query:
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