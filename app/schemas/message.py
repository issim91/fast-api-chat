from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    chat_id: int

class Message(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True 