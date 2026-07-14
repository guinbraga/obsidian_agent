import os
import json
import uuid
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from src.ingestion.models import Base, DocumentChunk

load_dotenv()


def get_engine():
    db_url = os.getenv("PSQL_CON_URL")
    return create_engine(db_url)


@contextmanager
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS obsidian_agent"))
    Base.metadata.create_all(engine)


# A unique UUID namespace for document chunks to ensure consistent uuid.uuid5 generation.
CHUNK_NAMESPACE = uuid.UUID("f3ab9292-628d-4be9-b4b6-7ebce2cf8608")


def generate_chunk_id(content: str, metadata: dict) -> uuid.UUID:
    # Serialize metadata with sorted keys for determinism
    metadata_str = json.dumps(metadata, sort_keys=True)
    unique_str = f"{metadata_str}:{content}"
    return uuid.uuid5(CHUNK_NAMESPACE, unique_str)


def insert_chunks(chunks, vectors):
    if not chunks:
        return

    data_to_insert = []
    for chunk, vector in zip(chunks, vectors):
        chunk_id = generate_chunk_id(chunk.page_content, chunk.metadata)
        data_to_insert.append({
            "id": chunk_id,
            "content": chunk.page_content,
            "metadata_": chunk.metadata,
            "embedding": vector,
        })

    with get_session() as session:
        stmt = insert(DocumentChunk).values(data_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        session.execute(stmt)
        print(f"Processed {len(data_to_insert)} chunks (skipped duplicates) in pgvector.")
