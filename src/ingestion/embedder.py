from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def load_embedder(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)


def create_embeddings(
    chunks: list[Document], embedder: HuggingFaceEmbeddings
) -> list[list[float]]:
    texts = [chunk.page_content for chunk in chunks]
    print(f"Generating vectors for {len(texts)} chunks...")
    vectors = embedder.embed_documents(texts)
    print(f"Succesfully generated {len(vectors)} vectors!")
    if vectors:
        print(f"length of first vector: {len(vectors[0])}")
    return vectors
