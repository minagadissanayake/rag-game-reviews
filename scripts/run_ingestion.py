import sys
import os
import re
from pathlib import Path

# Absolute paths - no ambiguity
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data" / "raw"
CHROMA_DIR = BACKEND_DIR / "chroma_db"

sys.path.append(str(BACKEND_DIR))

from app.ingestion.chunker import chunk_text
import chromadb
from sentence_transformers import SentenceTransformer

# Connect directly - bypass config entirely
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
model = SentenceTransformer("all-MiniLM-L6-v2")
collection = client.get_or_create_collection(
    name="game-reviews",
    metadata={"hnsw:space": "cosine"}
)

print(f"Data dir: {DATA_DIR}")
print(f"Chroma dir: {CHROMA_DIR}")

count = 0
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    slug = filename.replace(".txt", "")
    rating_match = re.search(r"Rating: ([\d.]+)", text)
    metacritic_match = re.search(r"Metacritic Score: (\d+)", text)
    genres_match = re.search(r"Genres: (.+)", text)

    metadata = {
        "source": filename,
        "slug": slug,
        "rating": float(rating_match.group(1)) if rating_match else 0.0,
        "metacritic": int(metacritic_match.group(1)) if metacritic_match else 0,
        "genres": genres_match.group(1) if genres_match else "",
    }

    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    ids = [f"{slug}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )
    count += 1
    print(f"Upserted {len(chunks)} chunks for: {slug}")

print(f"\nIngestion complete. {count} documents indexed.")
print(f"Total chunks in collection: {collection.count()}")