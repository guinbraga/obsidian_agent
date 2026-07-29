from langgraph.types import interrupt

from src.agent.state import AgentState


def human_gate(state: AgentState):
    preview = (
        f"Will {state.operations[0].action} note '{state.operations[0].note_name}'"
    )
    if state.dry_run:
        print(f"[DRY RUN] {preview}")
        return {"operations": state.operations}

    decision = interrupt(
        {
            "message": preview,
            "note_name": state.operations[0].note_name,
            "content_preview": state.draft_content[:200],
        }
    )

    if decision == "approve":
        return {"operations": state.operations}
    else:
        return {"operations": [], "errors": ["User rejected the operation"]}
