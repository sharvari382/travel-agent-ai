"""
FastAPI entrypoint.

Endpoints:
  POST /chat              -> send a message, get the agent's reply
  GET  /sessions          -> list all chat sessions (from ChromaDB metadata)
  GET  /sessions/{id}     -> get full history for one session
  GET  /search?q=...      -> semantic search across all past messages
"""
import uuid
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import memory, guardrails
from .schemas import ChatRequest, ChatResponse
from .agent import agent_executor

app = FastAPI(title="AI Travel Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1. Guardrail check on input
    check = guardrails.check_input(req.message)
    if not check.allowed:
        return ChatResponse(session_id=req.session_id or "", reply=check.message)

    # 2. Get or create session id
    session_id = req.session_id or str(uuid.uuid4())

    # 3. Load trimmed context window from ChromaDB
    chat_history = memory.load_history(session_id)

    # 4. Save the user's message
    memory.save_message(session_id, "user", req.message)

    # 5. Run the agent
    result = agent_executor.invoke({"input": req.message, "chat_history": chat_history})
    raw_reply = result["output"]

    # 6. Guardrail check on output
    reply = guardrails.check_output(raw_reply)

    # 7. Save assistant reply
    memory.save_message(session_id, "assistant", reply)

    return ChatResponse(session_id=session_id, reply=reply)


@app.get("/sessions")
def list_sessions():
    return memory.list_sessions()


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    return {"session_id": session_id, "messages": memory.load_full_session(session_id)}


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    """Semantic search across all past conversations."""
    return memory.semantic_search(q)
