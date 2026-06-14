import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_or_create_collection():
    return client.get_or_create_collection(
        name="game-reviews",
        metadata={"hnsw:space": "cosine"}
    )

def upsert_chunks(chunks: list[str], doc_id: str, metadata: dict = {}):
    collection = get_or_create_collection()
    embeddings = model.encode(chunks).tolist()
    ids = [f"{doc_id}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )
    print(f"Upserted {len(chunks)} chunks for doc: {doc_id}")