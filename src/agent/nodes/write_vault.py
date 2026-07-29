import os
from src.config import vault_path
from src.agent.state import AgentState

from pathlib import Path


def write_vault(state: AgentState):
    errors = []
    vault_dir = vault_path()
    for operation in state.operations:
        target = vault_dir / f"{operation.note_name}.md"
        try:
            if state.dry_run:
                print(f"[DRY RUN] Would write to {target}")
                continue
            if operation.action == "create" and not target.exists():
                temp_path = vault_dir / Path(f"tmp_{operation.note_name}.md")
                temp_path.write_text(state.draft_content)
                temp_path.rename(target)
            elif operation.action == "update" or target.exists():
                with target.open("a", encoding="utf-8") as note:
                    note.write(state.draft_content)
        except Exception as e:
            errors.append(f"Failed to write{target}: {e}")

    return {"errors": errors}
