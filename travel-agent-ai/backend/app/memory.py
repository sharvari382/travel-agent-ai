"""
Memory module — now backed entirely by ChromaDB.

Every message is added to the `chat_memory` collection with metadata.
- Exact context window: filter by session_id, sort by timestamp, take last N.
- Semantic recall (bonus capability you get for free): query the same
  collection by meaning across ALL sessions, e.g. "what did the user say
  about beach destinations before".
"""
import uuid
import datetime as dt
from langchain_core.messages import HumanMessage, AIMessage
from .chroma_client import chat_memory

MAX_TURNS_IN_CONTEXT = 12  # tune based on your model's context window


def save_message(session_id: str, role: str, content: str):
    msg_id = str(uuid.uuid4())
    chat_memory.add(
        ids=[msg_id],
        documents=[content],
        metadatas=[{
            "session_id": session_id,
            "role": role,
            "timestamp": dt.datetime.utcnow().isoformat(),
        }],
    )
    return msg_id


def load_history(session_id: str):
    """Return LangChain message objects for the most recent turns of a session,
    in chronological order, trimmed to MAX_TURNS_IN_CONTEXT."""
    results = chat_memory.get(
        where={"session_id": session_id},
        include=["documents", "metadatas"],
    )

    rows = list(zip(results["ids"], results["documents"], results["metadatas"]))
    rows.sort(key=lambda r: r[2]["timestamp"])

    trimmed = rows[-MAX_TURNS_IN_CONTEXT:]

    history = []
    for _id, content, meta in trimmed:
        if meta["role"] == "user":
            history.append(HumanMessage(content=content))
        elif meta["role"] == "assistant":
            history.append(AIMessage(content=content))
    return history


def load_full_session(session_id: str):
    """Full message list for a session, for the sidebar/history view in the UI."""
    results = chat_memory.get(
        where={"session_id": session_id},
        include=["documents", "metadatas"],
    )
    rows = list(zip(results["documents"], results["metadatas"]))
    rows.sort(key=lambda r: r[1]["timestamp"])
    return [{"role": meta["role"], "content": doc} for doc, meta in rows]


def list_sessions():
    """Distinct session_ids seen so far, with their first message as a title."""
    results = chat_memory.get(include=["documents", "metadatas"])
    sessions = {}
    for doc, meta in zip(results["documents"], results["metadatas"]):
        sid = meta["session_id"]
        if sid not in sessions or meta["timestamp"] < sessions[sid]["timestamp"]:
            sessions[sid] = {"session_id": sid, "title": doc[:50], "timestamp": meta["timestamp"]}
    return sorted(sessions.values(), key=lambda s: s["timestamp"], reverse=True)


def semantic_search(query: str, n_results: int = 5):
    """Search past messages across ALL sessions by meaning, not exact session."""
    results = chat_memory.query(query_texts=[query], n_results=n_results)
    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({"content": doc, "session_id": meta["session_id"], "role": meta["role"]})
    return hits
