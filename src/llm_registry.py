import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

DEFAULT_REGISTRY = {
    "STRONG": "deepseek-v4-flash",
    "FAST": "deepseek-v4-flash",
    "TOOL_CAPABLE": "deepseek-v4-flash",
}


class CapabilityRegistry:
    def __init__(self) -> None:
        self.llm_registry = DEFAULT_REGISTRY.copy()
        env_strong = os.getenv("LLM_STRONG")
        env_fast = os.getenv("LLM_FAST")
        env_tool_capable = os.getenv("LLM_TOOL_CAPABLE")
        if env_strong:
            self.llm_registry["STRONG"] = env_strong
        if env_fast:
            self.llm_registry["FAST"] = env_fast
        if env_tool_capable:
            self.llm_registry["TOOL_CAPABLE"] = env_tool_capable

    def get_model_id(
        self, capability: Literal["STRONG", "FAST", "TOOL_CAPABLE"] = "STRONG"
    ) -> str:
        valid_capabilities = ["STRONG", "FAST", "TOOL_CAPABLE"]
        if capability not in valid_capabilities:
            print("Unknown capability selected. Defaulting to STRONG model.")
            return self.llm_registry["STRONG"]
        return self.llm_registry[capability]
