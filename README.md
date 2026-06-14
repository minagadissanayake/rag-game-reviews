# RAG Game Reviews

A Retrieval-Augmented Generation (RAG) system that answers natural language questions about video games using a corpus of 364 game descriptions and metadata sourced from the RAWG API.

## What it does

Instead of keyword search, this system uses semantic embeddings to find the most relevant games for a query, then passes that context to GPT-4o-mini to generate a grounded, specific answer with citations.

Example queries:
- "What are some good dark atmospheric RPGs?"
- "I liked Hollow Knight, what should I play next?"
- "What are the highest rated strategy games on PC?"
- "Are there any co-op games with a Metacritic score above 90?"

## Tech Stack

- **Backend:** Python, FastAPI
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB:** ChromaDB
- **LLM:** OpenAI GPT-4o-mini
- **Data Source:** RAWG Video Games API

## Architecture

1. **Ingestion pipeline** — fetches game data from RAWG, chunks text, embeds with sentence-transformers, stores in Chroma
2. **Query pipeline** — embeds user query, retrieves top-5 semantically similar chunks, passes context to GPT-4o-mini, returns grounded answer with sources

## Setup

### Prerequisites
- Python 3.11
- RAWG API key (free at rawg.io/apidocs)
- OpenAI API key (platform.openai.com)

### Installation

```bash
git clone https://github.com/yourusername/rag-game-reviews
cd rag-game-reviews
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

### Build the index

```bash
# Fetch game data from RAWG
cd backend
python -m app.ingestion.loader

# Build the Chroma vector index
cd ..
python scripts/run_ingestion.py
```

### Run the API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to use the interactive API explorer.

### Query example

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are some good dark atmospheric RPGs?"}'
```

## Project Structure

```
rag-game-reviews/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # settings and env vars
│   │   ├── ingestion/
│   │   │   ├── loader.py     # fetch data from RAWG
│   │   │   ├── chunker.py    # split text into chunks
│   │   │   └── embedder.py   # embed and store in Chroma
│   │   ├── retrieval/
│   │   │   └── retriever.py  # semantic search
│   │   └── api/
│   │       └── routes.py     # /query endpoint
├── scripts/
│   └── run_ingestion.py      # build the vector index
├── data/raw/                  # game documents (gitignored)
├── .env.example
├── requirements.txt
└── README.md
```