from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.chat import ChatCreate, Chat
from app.schemas.message import Message
from app.schemas.group import GroupCreate, Group
from app.services.chat_service import ChatService
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=Chat)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    return await chat_service.create_chat(chat_data)

@router.post("/groups/", response_model=Group)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    return await chat_service.create_group(group_data, current_user.id)

@router.get("/{chat_id}/history", response_model=List[Message])
async def get_chat_history(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    chat_service = ChatService(db)
    return await chat_service.get_chat_history(chat_id, limit, offset, current_user) 
