from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


class Chunker(ABC):
    @abstractmethod
    def split(self, text: str, metadata: dict) -> list[Document]:
        pass


class RecursiveChunker(Chunker):
    def __init__(self, chunksize=1500, chunk_overlap=150):
        self.splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunksize=chunksize,
            chunk_overlap=chunk_overlap,
        )

    def split(self, text: str, metadata: dict) -> list[Document]:
        split_text = self.splitter.create_documents(texts=[text], metadatas=[metadata])
        return split_text


class MarkdownChunker(Chunker):
    def __init__(
        self, headers_to_split_on: list[tuple[str, str]] | None = None
    ) -> None:
        self.headers = headers_to_split_on or [("#", "Header 1"), ("##", "Header 2")]
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers, strip_headers=False
        )

    def split(self, text: str, metadata: dict) -> list[Document]:
        chunks = self.splitter.split_text(text)
        for chunk in chunks:
            chunk.metadata.update(metadata)
        return chunks
