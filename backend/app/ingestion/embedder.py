from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from app.config import settings
import uuid

_client = None
_openai = None

def get_client():
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
    return _client

def get_openai():
    global _openai
    if _openai is None:
        _openai = OpenAI(api_key=settings.openai_api_key)
    return _openai

def embed(texts: list[str]) -> list[list[float]]:
    response = get_openai().embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [r.embedding for r in response.data]

def get_or_create_collection():
    client = get_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.collection_name not in collections:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        print(f"Created collection: {settings.collection_name}")
    return client

def upsert_chunks(chunks: list[str], doc_id: str, metadata: dict = {}):
    client = get_or_create_collection()
    embeddings = embed(chunks)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[i],
            payload={**metadata, "text": chunks[i], "chunk_index": i}
        )
        for i in range(len(chunks))
    ]

    client.upsert(
        collection_name=settings.collection_name,
        points=points
    )
    print(f"Upserted {len(chunks)} chunks for doc: {doc_id}")