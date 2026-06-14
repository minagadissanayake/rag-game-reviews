import httpx
import os
import time
from dotenv import load_dotenv

load_dotenv()

RAWG_KEY = os.getenv("RAWG_API_KEY")
DATA_DIR = "./backend/data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_rawg_games(num_pages: int = 10) -> list[dict]:
    games = []
    for page in range(1, num_pages + 1):
        url = "https://api.rawg.io/api/games"
        params = {
            "key": RAWG_KEY,
            "ordering": "-rating",
            "page_size": 40,
            "page": page,
            "metacritic": "70,100",
        }
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        games.extend(data.get("results", []))
        print(f"Fetched page {page} - {len(games)} games so far")
        time.sleep(0.3)
    return games

def fetch_game_detail(game_slug: str) -> str:
    url = f"https://api.rawg.io/api/games/{game_slug}"
    resp = httpx.get(url, params={"key": RAWG_KEY}, timeout=15)
    if resp.status_code != 200:
        return ""
    return resp.json().get("description_raw", "")

def build_document(game: dict, description: str) -> str:
    genres = ", ".join([g["name"] for g in (game.get("genres") or [])])
    platforms = ", ".join([p["platform"]["name"] for p in (game.get("platforms") or [])])
    tags = ", ".join([t["name"] for t in (game.get("tags") or [])[:10]])

    return f"""Game: {game['name']}
Rating: {game.get('rating', 'N/A')} / 5 (based on {game.get('ratings_count', 0)} ratings)
Metacritic Score: {game.get('metacritic', 'N/A')}
Released: {game.get('released', 'N/A')}
Genres: {genres}
Platforms: {platforms}
Tags: {tags}

Description:
{description}
""".strip()

def run():
    games = fetch_rawg_games(num_pages=10)

    saved = 0
    for game in games:
        slug = game.get("slug", "")
        if not slug:
            continue

        description = fetch_game_detail(slug)
        if not description:
            continue

        doc = build_document(game, description)
        filepath = os.path.join(DATA_DIR, f"{slug}.txt")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(doc)

        saved += 1
        time.sleep(0.2)

    print(f"\nDone. {saved} documents saed to {DATA_DIR}")

if __name__ == "__main__":
    run()
