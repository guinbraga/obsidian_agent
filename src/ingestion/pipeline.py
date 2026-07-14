from langchain_core.documents import Document

from src.ingestion.parser import parse_textbook
from src.ingestion.embedder import create_embeddings
from src.ingestion.db import insert_chunks, init_db


def run_pipeline(file_path: str) -> None:
    init_db()
    print(f"Parsing {file_path}...")
    chunks: list[Document] = parse_textbook(file_path)
    print(f"Parsed {len(chunks)} chunks.")

    print("Creating embeddings...")
    vectors = create_embeddings(chunks)

    print("Inserting into database...")
    insert_chunks(chunks, vectors)
    print("Pipeline complete.")
