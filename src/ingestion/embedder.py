from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def create_embeddings(chunks: list[Document]) -> list[list[float]]:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    texts = [chunk.page_content for chunk in chunks]
    print(f"Generating vectors for {len(texts)} chunks...")
    vectors = embeddings.embed_documents(texts)
    print(f"Succesfully generated {len(vectors)} vectors!")
    print(f"length of first vector: {len(vectors[0])}")
    return vectors
