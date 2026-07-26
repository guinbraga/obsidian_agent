import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()


def vault_path() -> Path:
    raw = os.getenv("OBSIDIAN_VAULT_PATH")
    return Path(raw).expanduser().resolve()


def instantiate_embedder():
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embedder
