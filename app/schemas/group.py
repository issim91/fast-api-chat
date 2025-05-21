from pydantic import BaseModel
from datetime import datetime
from typing import List
from .user import User

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    chat_id: int
    creator_id: int
    created_at: datetime

    class Config:
        from_attributes = True 