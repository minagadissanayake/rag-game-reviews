from sentence_transformers import SentenceTransformer
from app.ingestion.embedder import get_or_create_collection, get_model
from app.config import settings

def retrieve(query: str) -> list[dict]:
    collection = get_or_create_collection()
    query_embedding = get_model().encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=settings.top_k,
        include=["documents", "metadatas", "distances"]
    )

    hits = []
    for i, doc in enumerate(results["documents"][0]):
        hits.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "score": round(1 - results["distances"][0][i], 4)
        })
    return hits