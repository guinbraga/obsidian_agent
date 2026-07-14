import re
from langchain_huggingface import HuggingFaceEmbeddings

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
    return final_chunks


def create_embeddings(chunks: list[Document]):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    texts = [chunk.page_content for chunk in chunks]
    print(f"Generating vectors for {len(texts)} chunks...")
    vectors = embeddings.embed_documents(texts)
    print(f"Succesfully generated {len(vectors)} vectors!")
    print(f"length of first vector: {len(vectors[0])}")
    return vectors
