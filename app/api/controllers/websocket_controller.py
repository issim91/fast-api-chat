from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.chat_service import ChatService
from app.core.database import get_db
from app.core.websocket_manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    await manager.connect(websocket, user_id)
    try:
        chat_service = ChatService(db)
        await chat_service.handle_websocket_connection(websocket, user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id) 