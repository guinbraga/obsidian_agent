import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector


Base = declarative_base()


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = {"schema": "obsidian_agent"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    metadata_ = Column(
        "metadata", JSONB, nullable=False
    )  # mapped because it's a reserved word
    embedding = Column(Vector(384), nullable=False)
