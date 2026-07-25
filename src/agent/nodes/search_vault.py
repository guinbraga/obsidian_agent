from src.ingestion.knowledge_base import KnowledgeBase
from src.agent.state import AgentState


def search_vault(state: AgentState):
    kb = KnowledgeBase()
    results = kb.search(query=state.user_prompt, source_type="vault_note")
    vault_results = [
        {"note_metadata": chunk.metadata_, "similarity": 1 - distance}
        for chunk, distance in results
    ]
    return {"vault_results": vault_results}
