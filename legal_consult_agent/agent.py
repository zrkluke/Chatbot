from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from legal_consult_agent.nodes import (
    semantic_router,
    retriever,
    generator,
    critic,
    reranker,
)
from legal_consult_agent.utils.state import LegalConsultState as State

builder = StateGraph(State)
builder.add_node("semantic_router", semantic_router)
builder.add_node("retriever", retriever)
builder.add_node("generator", generator)
builder.add_node("critic", critic)
builder.add_node("reranker", reranker)

builder.add_edge(START, "semantic_router")
builder.add_conditional_edges(
    source="semantic_router",
    path=lambda state: state["Retrieve"],
    path_map={
        "Yes": "retriever",
        "No": "generator",
    }
)
builder.add_edge("retriever", "generator")
builder.add_edge("generator", "critic")
builder.add_conditional_edges(
    source="critic",
    path=lambda state: state["Retrieve"],
    path_map={
        "Yes": "reranker",
        "No": END,
    }
)
builder.add_edge("reranker", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
graph.get_graph().print_ascii()
