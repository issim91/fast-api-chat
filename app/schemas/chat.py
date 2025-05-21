from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.chat import ChatType

class ChatBase(BaseModel):
    name: Optional[str] = None
    type: ChatType

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 