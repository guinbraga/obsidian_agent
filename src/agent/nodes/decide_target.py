from typing import Literal

from src.agent.state import AgentState, VaultOperation


def decide_target(state: AgentState):
    similarity_threshold = 0.90
    possible_notes = state.vault_results

    if possible_notes is None:
        operation = VaultOperation(action="create", note_name="RAG Deep Dive")
        return {"operations": [operation]}

    similar_notes = [
        note for note in possible_notes if note["similarity"] > similarity_threshold
    ]
    if similar_notes:
        operation = VaultOperation(action="update", note_name="RAG Overview")
        return {"operations": [operation]}
    else:
        operation = VaultOperation(action="create", note_name="RAG Deep Dive")
        return {"operations": [operation]}


def has_operations(state: AgentState) -> Literal["generate", "end"]:
    if state.operations:
        return "generate"
    return "end"
