from typing import Literal, Optional

from pydantic import BaseModel


class VaultOperation(BaseModel):
    action: Literal["create", "update"]
    note_name: str
    content: str = ""


class AgentState(BaseModel):
    # inputs
    user_prompt: str
    dry_run: bool = False

    vault_results: Optional[list[dict]] = None
    context_results: list[dict] = []

    operations: list[VaultOperation] = []
    draft_content: Optional[str] = None
    errors: list[str] = []

    cascade_count: int = 0
    cascade_limit: int = 2
