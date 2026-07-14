"""Ingestion package for processing and storing textbook documents."""

from src.ingestion.models import DocumentChunk
from src.ingestion.parser import clean_pdf_markdown, parse_textbook
from src.ingestion.embedder import create_embeddings
from src.ingestion.db import get_engine, get_session, insert_chunks
from src.ingestion.pipeline import run_pipeline

__all__ = [
    "DocumentChunk",
    "clean_pdf_markdown",
    "parse_textbook",
    "create_embeddings",
    "get_engine",
    "get_session",
    "insert_chunks",
    "run_pipeline",
]
