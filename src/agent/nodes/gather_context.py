from src.ingestion.knowledge_base import KnowledgeBase
from src.agent.state import AgentState


def gather_context(state: AgentState):
    kb = KnowledgeBase()
    results = kb.search(query=state.user_prompt, source_type="textbook")
    context_results = [
        {"metadata": chunk.metadata_, "content": chunk.content} for chunk, _ in results
    ]
    return {"context_results": context_results}
