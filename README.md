# GameVaultAI

> AI-powered game recommendation engine — ask anything, get answers grounded in real reviews.

**Live:** [gamevaultai.vercel.app](https://gamevaultai.vercel.app) · **API:** [gamevaultai.onrender.com](https://gamevaultai.onrender.com/docs)

![GameVaultAI](./screenshot.png)

---

## What it does

GameVaultAI lets you find your next favorite game using natural language. Instead of browsing lists or filtering by genre, you describe what you're looking for — a vibe, a mood, a game you already loved — and get a grounded, specific answer backed by real review data.

Unlike a keyword search, GameVaultAI understands meaning. Ask *"something like Dark Souls but less punishing"* and it finds games that semantically match that description across a corpus of 1,916 indexed titles.

It also maintains conversational context — ask a follow-up like *"which of those is the most recent?"* and it answers using the previous response.

---

## How it works

```
User query
    │
    ▼
Embed query          ← OpenAI text-embedding-3-small
    │
    ▼
Vector search        ← Qdrant Cloud (1,916 games, cosine similarity)
    │
    ▼
Retrieve top-10      ← most semantically relevant game chunks
    │
    ▼
Generate answer      ← GPT-4o-mini with retrieved context + conversation history
    │
    ▼
Return answer + sources
```

This is a **Retrieval-Augmented Generation (RAG)** architecture. The LLM never answers from its own training data alone — every recommendation is grounded in the indexed corpus.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector DB | Qdrant Cloud |
| LLM | OpenAI GPT-4o-mini |
| Data source | RAWG Video Games API |
| Frontend | React, Vite |
| Backend deploy | Render |
| Frontend deploy | Vercel |

---

## Features

- **Semantic search** — finds games by meaning, not just keywords
- **Conversational context** — follow-up questions use previous answers
- **1,916 games indexed** — top-rated titles across all genres and platforms
- **Grounded answers** — LLM only recommends games from the retrieved corpus
- **Source attribution** — every answer shows which games were used as context
- **Keyboard shortcut** — press `/` to focus the search input

---

## Project structure

```
rag-game-reviews/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS
│   │   ├── config.py            # pydantic settings
│   │   ├── ingestion/
│   │   │   ├── loader.py        # fetch game data from RAWG API
│   │   │   ├── chunker.py       # split text into chunks
│   │   │   └── embedder.py      # embed + upsert to Qdrant
│   │   ├── retrieval/
│   │   │   └── retriever.py     # semantic search against Qdrant
│   │   └── api/
│   │       └── routes.py        # POST /query endpoint
├── frontend/
│   └── src/
│       ├── App.jsx              # main React component
│       └── index.css            # styles
├── scripts/
│   └── run_ingestion.py         # build the vector index
├── .env.example
├── requirements.txt
└── README.md
```

---

## Local setup

### Prerequisites

- Python 3.11
- Node.js 18+
- [RAWG API key](https://rawg.io/apidocs) — free
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Qdrant Cloud](https://cloud.qdrant.io) account — free tier

### 1. Clone and install

```bash
git clone https://github.com/minagadissanayake/rag-game-reviews
cd rag-game-reviews

python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in your `.env`:

```
RAWG_API_KEY=your-rawg-key
OPENAI_API_KEY=your-openai-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
EMBEDDING_MODEL=text-embedding-3-small
COLLECTION_NAME=game-reviews
LLM_MODEL=gpt-4o-mini
TOP_K=10
```

### 3. Build the index

```bash
# Fetch game data from RAWG (~10 min for 2000 games)
cd backend
python -m app.ingestion.loader

# Embed and index into Qdrant (~15 min)
cd ..
python scripts/run_ingestion.py
```

### 4. Run the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## API reference

### `POST /api/query`

Ask a question and get a grounded game recommendation.

**Request**
```json
{
  "question": "What are the best dark atmospheric RPGs?",
  "history": [
    { "role": "user", "content": "previous question" },
    { "role": "assistant", "content": "previous answer" }
  ]
}
```

**Response**
```json
{
  "answer": "Based on the indexed games, here are some great dark atmospheric RPGs...",
  "sources": [
    {
      "text": "Game: Planescape Torment...",
      "metadata": {
        "slug": "planescape-torment",
        "rating": 4.34,
        "metacritic": 91,
        "genres": "Strategy, RPG"
      },
      "score": 0.847
    }
  ]
}
```

### `GET /health`

Returns `{ "status": "ok" }` — used for uptime monitoring.

---

## Deployment

The backend is deployed on **Render** (free tier). Note that Render's free tier spins down after 15 minutes of inactivity — the first request after a period of no use may take 30-60 seconds as the service wakes up.

The frontend is deployed on **Vercel** with automatic deploys on every push to `main`.

The vector database is hosted on **Qdrant Cloud** (free tier) and persists independently of both deploys.

---

## Design decisions

**Why RAG instead of fine-tuning?**
Fine-tuning a model on game data would be expensive and inflexible — adding new games would require retraining. RAG lets us update the corpus by just re-running the ingestion script.

**Why OpenAI embeddings instead of a local model?**
`text-embedding-3-small` produces high-quality 1536-dim embeddings via API, eliminating the memory overhead of running a local model. On Render's free tier (512MB RAM), a local sentence-transformers model causes OOM crashes.

**Why Qdrant over ChromaDB?**
ChromaDB is file-based and doesn't persist across Render deploys. Qdrant Cloud gives a free hosted vector DB that survives redeploys and scales independently.

**Why GPT-4o-mini?**
Fast, cheap, and smart enough for recommendation tasks. At ~$0.00015 per query it's practically free for a portfolio project.

---

## Author

**Minaga Dissanayake**
[github.com/minagadissanayake](https://github.com/minagadissanayake)