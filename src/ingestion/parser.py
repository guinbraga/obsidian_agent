import re
import fitz

import os
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from llama_cloud import LlamaCloud

load_dotenv()

llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")


def clean_pdf_markdown(text: str) -> str:
    text = re.sub(r"(\w+)[-\u2010]+\s+(\w+)", r"\1\2", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def parse_textbook_llama(file_path: str) -> list[Document]:
    client = LlamaCloud(api_key=llama_api_key)
    print("Parsing file with LlamaCloud...")
    file = client.files.create(file=file_path, purpose="parse")
    parsed_file = client.parsing.parse(
        file_id=file.id, tier="agentic", version="latest", expand=["markdown"]
    )
    all_file_pages = "\n\n".join([page.markdown for page in parsed_file.markdown.pages])

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

def parse_textbook_pymupdf(file_path: str):
    """
    Extracts text from a PDF and chunks it for the vector database.
    Uses PyMuPDF, which is a cheaper and cost-efficient alternative to LlamaCloud.
    """
    print(f"Extracting text locally using PyMuPDF from {file_path}...")

    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n\n"

    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            length_function=len,
            )

    chunks = text_splitter.split_text(full_text)
    print(f"Successfully created {len(chunks)} chunks!")

    return chunks
