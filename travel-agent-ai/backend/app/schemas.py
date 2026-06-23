from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None   # if None, a new session is created
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
