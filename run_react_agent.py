import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_community.tools import DuckDuckGoSearchRun

# Import the search_textbook tool from Lesson 2
from run_tool_check import search_textbook
from obsidian_tools import read_obsidian_note, append_obsidian_note

load_dotenv()


# 1. State Definition
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# 2. Setup LLM & Bind Tools
api_key = os.getenv("OPENCODE_API_KEY")

if not api_key or api_key == "your_opencode_go_api_key_here":
    print(
        "❌ ERROR: Please replace the OPENCODE_API_KEY placeholder in your .env file with your actual OpenCode Go API key!"
    )
    exit(1)

llm = ChatOpenAI(
    base_url="https://opencode.ai/zen/go/v1", api_key=api_key, model="deepseek-v4-flash"
)

# Bind both search tools
tools = [
    search_textbook,
    DuckDuckGoSearchRun(),
    read_obsidian_note,
    append_obsidian_note,
]
llm_with_tools = llm.bind_tools(tools)


# 3. Define Nodes
def agent_node(state: AgentState):
    print("--- [Agent Node]: Thinking... ---")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# 4. Construct Graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# Compile
graph = builder.compile()


def run_agent(query: str):
    """Executes the agent graph with the given query and prints the output."""
    print(f"Asking Agent: '{query}'\n")
    events = graph.stream({"messages": [{"role": "user", "content": query}]})
    for event in events:
        for node_name, state in event.items():
            print(f"\n=== Node Completed: {node_name} ===")
            if "messages" in state:
                last_msg = state["messages"][-1]
                content = (
                    last_msg.content if last_msg.content else str(last_msg.tool_calls)
                )
                print(f"[{last_msg.type.upper()}]: {content[:500]}")


if __name__ == "__main__":
    run_agent("Test query")
