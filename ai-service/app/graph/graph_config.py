from langgraph.checkpoint.memory import MemorySaver

from app.graph.advisor_graph import create_advisor_graph

_checkpointer = MemorySaver()
_graph = None


def get_advisor_graph():
    """Get the compiled advisor graph with checkpointer.

    Returns a singleton graph instance with MemorySaver for thread-level persistence.
    """
    global _graph
    if _graph is None:
        _graph = create_advisor_graph()
    return _graph


def get_graph_config(session_id: str) -> dict:
    """Get the LangGraph config for a given session.

    Args:
        session_id: UUID for the conversation session.

    Returns:
        Config dict with thread_id for LangGraph checkpointing.
    """
    return {"configurable": {"thread_id": session_id}}
