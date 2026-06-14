from app.ingestion.embedder import get_client, embed
from app.config import settings

def retrieve(query: str) -> list[dict]:
    client = get_client()
    query_embedding = embed([query])[0]

    results = client.search(
        collection_name=settings.collection_name,
        query_vector=query_embedding,
        limit=settings.top_k,
        with_payload=True
    )

    hits = []
    for r in results:
        payload = dict(r.payload)
        text = payload.pop("text", "")
        hits.append({
            "text": text,
            "metadata": payload,
            "score": round(r.score, 4)
        })
    return hits