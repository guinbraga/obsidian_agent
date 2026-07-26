from langgraph.graph import StateGraph, START, END
from src.agent.nodes.generate_content import generate_content
from src.agent.nodes.search_vault import search_vault
from src.agent.nodes.decide_target import decide_target, has_operations
from src.agent.state import AgentState


builder = StateGraph(AgentState)

builder.add_node("search_vault", search_vault)
builder.add_node("decide_target", decide_target)
builder.add_node("generate_content", generate_content)

builder.add_edge(START, "search_vault")
builder.add_edge("search_vault", "decide_target")
builder.add_conditional_edges(
    "decide_target", has_operations, {"generate": "generate_content", "end": END}
)
builder.add_edge("generate_content", END)

graph = builder.compile()

prompts = [
    "Make a note on RAG",
    "Make a note on chairs",
    "Write about the chi squared test.",
]
for prompt in prompts:
    result = graph.invoke({"user_prompt": prompt})
    print(
        f"State operations: {result['operations']}\n State draft_content: {result['draft_content']}"
    )
