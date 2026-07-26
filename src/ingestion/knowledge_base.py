from langchain_core.documents import Document
from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert

from src.config import instantiate_embedder
from src.ingestion.db import generate_chunk_id
from src.ingestion import DocumentChunk, create_embeddings, get_session


class KnowledgeBase:
    def search(self, query: str, source_type: str = "textbook", top_k: int = 5):
        query_doc = Document(page_content=query)
        query_embed = create_embeddings([query_doc], embedder=instantiate_embedder())[0]

        stmt = (
            select(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_embed).label("distance"),
            )
            .order_by(DocumentChunk.embedding.cosine_distance(query_embed))
            .limit(top_k)
        )

        if source_type == "textbook" or source_type is None:
            stmt = stmt.where(
                or_(
                    DocumentChunk.source_type == "textbook",
                    DocumentChunk.source_type.is_(None),
                )
            )

        elif source_type:
            stmt = stmt.where(DocumentChunk.source_type == source_type)

        with get_session() as session:
            results = session.execute(stmt).all()
            # Eagerly extract data into plain dicts before session closes
            return [
                {
                    "content": row.DocumentChunk.content,
                    "metadata_": row.DocumentChunk.metadata_,
                    "source_type": row.DocumentChunk.source_type,
                    "distance": row.distance,
                }
                for row in results
            ]

    def insert(self, chunks, vectors, source_type):
        if not chunks:
            return

        data_to_insert = []
        for chunk, vector in zip(chunks, vectors):
            chunk_id = generate_chunk_id(chunk.page_content, chunk.metadata)
            data_to_insert.append(
                {
                    "id": chunk_id,
                    "content": chunk.page_content,
                    "metadata_": chunk.metadata,
                    "embedding": vector,
                    "source_type": source_type,
                }
            )

        with get_session() as session:
            stmt = insert(DocumentChunk).values(data_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            session.execute(stmt)
            print(
                f"Processed {len(data_to_insert)} chunks (skipped duplicates) to pgvector"
            )

    def delete_by_source(self, source: str, source_type: str = "vault_note"):
        with get_session() as session:
            stmt = (
                delete(DocumentChunk)
                .where(DocumentChunk.source_type == source_type)
                .where(DocumentChunk.metadata_["source"].astext == source)
            )
            result = session.execute(stmt)
            print(f"Deleted {result.rowcount} old chunks for {source}")
