from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base

class ChatType(enum.Enum):
    PRIVATE = "private"
    GROUP = "group"

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Optional for private chats
    type = Column(Enum(ChatType), default=ChatType.PRIVATE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="chat")
    group = relationship("Group", back_populates="chat", uselist=False) 