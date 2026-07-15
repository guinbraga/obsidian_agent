import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from src.ingestion.db import get_session
from src.ingestion.models import DocumentChunk

# Load variables from .env
load_dotenv()

# 1. Define the Vector Search Tool
@tool
def search_textbook(query: str) -> str:
    """Useful for retrieving technical information about AI engineering, RAG, and evaluation metrics from the textbook database."""
    print(f"\n--- [Tool Triggered]: search_textbook for query '{query}' ---")
    
    # Generate query embedding
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    query_vector = embeddings.embed_query(query)
    
    # Query pgvector in database
    with get_session() as session:
        results = (
            session.query(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(3)
            .all()
        )
        
        # Format results as a readable string
        docs = []
        for i, r in enumerate(results):
            docs.append(f"Result {i+1}:\n{r.content}\nMetadata: {r.metadata_}\n---")
        return "\n\n".join(docs)

# 2. Setup LLM and bind tool
api_key = os.getenv("OPENCODE_API_KEY")

if not api_key or api_key == "your_opencode_go_api_key_here":
    print("❌ ERROR: Please replace the OPENCODE_API_KEY placeholder in your .env file with your actual OpenCode Go API key!")
    exit(1)

print("Connecting to OpenCode Go model (glm-5.2)...")
llm = ChatOpenAI(
    base_url="https://opencode.ai/zen/go/v1",
    api_key=api_key,
    model="glm-5.2"
)

# Bind tool to the model
llm_with_tools = llm.bind_tools([search_textbook])

if __name__ == "__main__":
    print("\n--- Running Test 1: Simple Greeting (Should NOT call tool) ---")
    response_greeting = llm_with_tools.invoke("Hi, how are you?")
    print("Greeting Response:", response_greeting.content)
    print("Greeting Tool Calls:", response_greeting.tool_calls)
    
    print("\n--- Running Test 2: RAG Question (SHOULD call tool) ---")
    response_rag = llm_with_tools.invoke("What are some evaluation metrics for RAG?")
    print("RAG Response Content (if returned immediately):", response_rag.content)
    print("RAG Tool Calls:", response_rag.tool_calls)
