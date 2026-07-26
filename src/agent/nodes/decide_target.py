import os
from dotenv import load_dotenv
from collections import defaultdict
from pathlib import Path
import re
from typing import Literal

from src.agent.state import AgentState, VaultOperation

# ==== Helper Functions =======


def load_policy():
    load_dotenv()
    policy = {
        "create_threshold": float(os.getenv("CREATE_THRESHOLD")),
        "update_threshold": float(os.getenv("UPDATE_THRESHOLD")),
        "ambiguous_action": os.getenv("AMBIGUOUS_ACTION"),
        "note_name_strategy": os.getenv("NOTE_NAME_STRATEGY"),
    }
    return policy


def extract_topic(prompt: str) -> str:
    pattern = r"(?:about|on|regarding|for|discussing)\s+(.+)"
    match = re.search(pattern, prompt, re.IGNORECASE)

    INVALID_CHARS = r"[\\/:*?<>|]"

    if match:
        topic = match.group(1).rstrip(".!?;")
        topic = re.sub(INVALID_CHARS, "-", topic)  # make file-name ready
        return topic[:50].title()

    fallback = prompt.strip().rstrip(".!?;")
    fallback = re.sub(INVALID_CHARS, "-", fallback)
    return fallback[:50].title()


def decide_target(state: AgentState):
    policy = load_policy()
    target_selector = TargetSelector(policy)
    selected_operations = target_selector.select(state)
    return {"operations": selected_operations}


def has_operations(state: AgentState) -> Literal["generate", "end"]:
    if state.operations:
        return "generate"
    return "end"


class TargetSelector:
    def __init__(self, policy: dict):
        self.policy = policy

    def select(self, state: AgentState) -> list[VaultOperation]:
        vault_results = state.vault_results
        if not vault_results:
            return [
                VaultOperation(
                    action="create", note_name=extract_topic(state.user_prompt)
                )
            ]
        groups = defaultdict(list)
        for result in vault_results:
            source = result["note_metadata"]["source"]
            groups[source].append(result)

        best_per_group = []
        for source, items in groups.items():
            best = max(items, key=lambda r: r["similarity"])
            best_per_group.append(
                {
                    "source": source,
                    "best_similarity": best["similarity"],
                    "best_metadata": best["note_metadata"],
                }
            )
        highest_match = sorted(
            best_per_group, key=lambda r: r["best_similarity"], reverse=True
        )[0]

        if highest_match["best_similarity"] >= self.policy["update_threshold"]:
            action = "update"
        elif highest_match["best_similarity"] <= self.policy["create_threshold"]:
            action = "create"
        else:
            action = self.policy["ambiguous_action"]

        if action == "update":
            note_name = Path(highest_match["source"]).stem  # always the matched file
        elif action == "create":
            strategy = self.policy.get("note_name_strategy", "from_prompt")
            if strategy == "from_prompt":
                note_name = extract_topic(state.user_prompt)
            elif strategy == "from_match":
                note_name = Path(highest_match["source"]).stem
            elif strategy == "fixed":
                note_name = self.policy.get("fixed_note_name", "Untitled")
            else:
                note_name = extract_topic(state.user_prompt)  # sensible fallback
        elif action == "skip":
            return []
        else:
            raise Exception(f"action must be 'update' or 'create', but was {action}")
        return [VaultOperation(action=action, note_name=note_name)]
