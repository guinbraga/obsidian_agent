from langchain_core.documents import Document

from src.ingestion.parser import parse_textbook_llama, parse_textbook_pymupdf
from src.ingestion.embedder import create_embeddings
from src.ingestion.db import insert_chunks, init_db


def run_pipeline(file_path: str, textbook_parser: str = "pymupdf") -> None:
    init_db()
    print(f"Parsing {file_path}...")
    if textbook_parser == "pymupdf":
        chunks = parse_textbook_pymupdf(file_path)
    elif textbook_parser == "llamacloud":
        chunks = parse_textbook_llama(file_path)
    else:
        return

    print(f"Parsed {len(chunks)} chunks.")

    print("Creating embeddings...")
    vectors = create_embeddings(chunks)

    print("Inserting into database...")
    insert_chunks(chunks, vectors)
    print("Pipeline complete.")
