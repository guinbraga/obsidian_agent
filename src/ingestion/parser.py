import re

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from llama_cloud import LlamaCloud


def clean_pdf_markdown(text: str) -> str:
    text = re.sub(r"(\w+)[-\u2010]+\s+(\w+)", r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def parse_textbook(file_path: str) -> list[Document]:
    client = LlamaCloud()
    file = client.files.create(file=file_path, purpose="parse")
    parsed_file = client.parsing.parse(
        file_id=file.id, tier="agentic", version="latest", expand=["markdown"]
    )
    all_file_pages = "\n\n".join(
        [page.markdown for page in parsed_file.markdown.pages]
    )

    clean_markdown = clean_pdf_markdown(all_file_pages)

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Chapter"), ("##", "Section")],
        strip_headers=False,
    )
    document_chunks = header_splitter.split_text(clean_markdown)

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=150, separators=["\n\n", "\n", " ", ""]
    )
    final_chunks = recursive_splitter.split_documents(document_chunks)

    import os
    source_filename = os.path.basename(file_path)
    for chunk in final_chunks:
        chunk.metadata["source"] = source_filename

    return final_chunks

