from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    openai_api_key: str
    rawg_api_key: str
    chroma_persist_dir: str = str(ROOT_DIR / "backend" / "chroma_db")
    embedding_model: str = "all-MiniLM-L6-v2"
    collection_name: str = "game-reviews"
    llm_model: str = "gpt-4o-mini"
    top_k: int = 5

    class Config:
        env_file = str(ROOT_DIR / ".env")

settings = Settings()