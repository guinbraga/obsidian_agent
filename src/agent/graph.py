from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from src.agent.nodes.decide_target import decide_target, has_operations
from src.agent.nodes.generate_content import generate_content
from src.agent.nodes.human_gate import human_gate
from src.agent.nodes.search_vault import search_vault
from src.agent.nodes.write_vault import write_vault
from src.agent.state import AgentState

builder = StateGraph(AgentState)

builder.add_node("search_vault", search_vault)
builder.add_node("decide_target", decide_target)
builder.add_node("generate_content", generate_content)
builder.add_node("write_vault", write_vault)
builder.add_node("human_gate", human_gate)

builder.add_edge(START, "search_vault")
builder.add_edge("search_vault", "decide_target")
builder.add_conditional_edges(
    "decide_target", has_operations, {"generate": "generate_content", "end": END}
)
builder.add_edge("generate_content", "human_gate")
builder.add_edge("human_gate", "write_vault")
builder.add_edge("write_vault", END)

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "thread-1"}}

prompts = [
    "Make a note on REG",
    "Make a note on ch4irs",
    "Write about the ch2 squared test.",
]
for prompt in prompts:
    result = graph.invoke(
        {"user_prompt": prompt, "dry_run": True},
        config=config,
    )
    if result.get("__interrupt__", False):
        for interrupt in result["__interrupt__"]:
            print(interrupt)
            user_input = input("Approve? (y/n): ")
            decision = "approve" if user_input.lower() == "y" else "reject"
            result = graph.invoke(Command(resume=decision), config=config)
    print(
        f"State operations: {result['operations']}\n State draft_content: {result['draft_content']}"
    )
