import chromadb
from pathlib import Path

CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"

_client = None
_model = None

def get_client():
    global _client
    if _client is None:
        try:
            _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        except Exception as e:
            print(f"Chroma init failed: {e}")
            raise
    return _client

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_or_create_collection():
    return get_client().get_or_create_collection(
        name="game-reviews",
        metadata={"hnsw:space": "cosine"}
    )

def upsert_chunks(chunks: list[str], doc_id: str, metadata: dict = {}):
    collection = get_or_create_collection()
    embeddings = get_model().encode(chunks).tolist()
    ids = [f"{doc_id}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )
    print(f"Upserted {len(chunks)} chunks for doc: {doc_id}")