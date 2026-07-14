import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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


def insert_chunks(chunks, vectors):
    with get_session() as session:
        chunks_to_insert = []
        for chunk, vector in zip(chunks, vectors):
            new_row = DocumentChunk(
                content=chunk.page_content,
                metadata_=chunk.metadata,
                embedding=vector,
            )
            chunks_to_insert.append(new_row)

        session.add_all(chunks_to_insert)
        print(f"Inserted {len(chunks_to_insert)} chunks into pgvector.")
