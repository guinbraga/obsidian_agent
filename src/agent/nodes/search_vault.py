import os
from pathlib import Path

from dotenv import load_dotenv

from src.config import vault_path
from src.agent.state import AgentState
from src.ingestion.knowledge_base import KnowledgeBase
from src.ingestion.vault_indexer import VaultIndexer

load_dotenv()


def search_vault(state: AgentState):
    kb = KnowledgeBase()
    vault_indexer = VaultIndexer(vault_path())
    vault_indexer.index()
    results = kb.search(query=state.user_prompt, source_type="vault_note")
    vault_results = [
        {"note_metadata": row["metadata_"], "similarity": 1 - row["distance"]}
        for row in results
    ]
    return {"vault_results": vault_results}
