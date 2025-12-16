from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Chat Session Schemas
class ChatSessionBase(BaseModel):
    title: str
    user_id: Optional[str] = None
    is_active: Optional[bool] = True


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None


class ChatSession(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    session_id: int
    role: str  # 'user' or 'assistant'
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSession):
    messages: List[ChatMessage] = []


# Chat Request/Response Schemas
class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    query: str
    mode: str = "global"  # "global" or "selected_text_only"
    selected_text: Optional[str] = ""


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    session_id: int