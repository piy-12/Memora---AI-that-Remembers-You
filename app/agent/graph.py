from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.context import Context
from app.agent.nodes import chatbot


def create_graph(checkpointer, store):

    builder = StateGraph(
        AgentState,
        context_schema=Context
    )

    builder.add_node("chatbot", chatbot)

    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    graph = builder.compile(
        checkpointer=checkpointer,
        store=store
    )

    return graph