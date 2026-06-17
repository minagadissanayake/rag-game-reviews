import sys
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data" / "raw"
DATA_DIR_ALT = BACKEND_DIR / "backend" / "data" / "raw"

sys.path.append(str(BACKEND_DIR))

from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import upsert_chunks, get_or_create_collection, get_client
from app.config import settings

def get_indexed_slugs() -> set:
    """Fetch all slugs already in Qdrant so we can skip them."""
    client = get_client()
    indexed = set()
    offset = None
    batch_size = 100

    while True:
        results, next_offset = client.scroll(
            collection_name=settings.collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=["slug"],
            with_vectors=False
        )

        for point in results:
            slug = point.payload.get("slug")
            if slug:
                indexed.add(slug)

        if next_offset is None:
            break
        offset = next_offset

    return indexed

# Make sure collection exists
get_or_create_collection()

print("Fetching already-indexed slugs from Qdrant...")
indexed_slugs = get_indexed_slugs()
print(f"Already indexed: {len(indexed_slugs)} documents")

all_files = (
    [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    + [f for f in os.listdir(DATA_DIR_ALT) if f.endswith(".txt")]
)

# Deduplicate filenames in case same file exists in both dirs
all_files = list(set(all_files))

skipped = 0
count = 0

for filename in all_files:
    slug = filename.replace(".txt", "")

    if slug in indexed_slugs:
        skipped += 1
        continue

    # Check both directories
    filepath = DATA_DIR / filename
    if not filepath.exists():
        filepath = DATA_DIR_ALT / filename

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

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

print(f"\nDone. {count} new documents indexed, {skipped} already existed — skipped.")