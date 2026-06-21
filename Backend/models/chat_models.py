# chat_models.py
# Pydantic models define the *shape* of data we expect to receive or send.
# FastAPI uses these to automatically validate incoming requests and reject
# anything that doesn't match — before our own code even runs.

from pydantic import BaseModel
from typing import Optional

class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"  # if not provided, defaults to "New Chat"

class MessageCreate(BaseModel):
    role: str       # expected to be "user" or "assistant"
    content: str    # the actual message text
class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str