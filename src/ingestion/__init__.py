"""Ingestion package for processing and storing textbook documents."""

from src.ingestion.models import DocumentChunk
from src.ingestion.parser import (
    clean_pdf_markdown,
    parse_textbook_llama,
    parse_textbook_pymupdf,
)
from src.ingestion.embedder import create_embeddings, load_embedder
from src.ingestion.db import get_engine, get_session, insert_chunks
from src.ingestion.pipeline import run_pipeline

__all__ = [
    "DocumentChunk",
    "clean_pdf_markdown",
    "parse_textbook_llama",
    "parse_textbook_pymupdf",
    "create_embeddings",
    "get_engine",
    "get_session",
    "insert_chunks",
    "run_pipeline",
]
