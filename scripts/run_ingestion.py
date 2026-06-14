import sys
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data" / "raw"

sys.path.append(str(BACKEND_DIR))

from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import upsert_chunks, get_or_create_collection

# Make sure collection exists
get_or_create_collection()

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
    upsert_chunks(chunks, doc_id=slug, metadata=metadata)
    count += 1
    print(f"Indexed {count}: {slug}")

print(f"\nDone. {count} documents indexed to Qdrant Cloud.")