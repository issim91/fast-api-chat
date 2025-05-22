from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from typing import List
from app.models.user import User
from app.models.chat import Chat, ChatType
from app.models.group import Group
from app.models.message import Message
from app.schemas.chat import ChatCreate
from app.schemas.group import GroupCreate
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.group_repository import GroupRepository
from app.core.websocket_manager import manager

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.message_repository = MessageRepository(db)
        self.group_repository = GroupRepository(db)

    async def create_chat(self, chat_data: ChatCreate):
        chat = await self.chat_repository.create(
            name=chat_data.name,
            type=chat_data.type
        )
        return chat

    async def create_group(self, group_data: GroupCreate, current_user_id: int):
        # Создаем чат для группы
        chat = await self.chat_repository.create(type=ChatType.GROUP)

        # Создаем группу
        group = await self.group_repository.create(
            chat_id=chat.id,
            creator_id=current_user_id,
            name=group_data.name
        )

        # Добавляем создателя в группу
        await self.group_repository.add_member(group.id, current_user_id)
        return group

    async def get_chat_history(
        self,
        chat_id: int,
        limit: int,
        offset: int,
        current_user: User
    ) -> List[Message]:
        # Проверяем доступ к чату
        if not await self.chat_repository.has_access(chat_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return await self.message_repository.get_chat_messages(
            chat_id=chat_id,
            limit=limit,
            offset=offset
        )

    async def handle_websocket_connection(self, websocket: WebSocket, user_id: int):
        await manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_json()
                
                if data["type"] == "message":
                    # Создаем сообщение
                    message = await self.message_repository.create(
                        chat_id=data["chat_id"],
                        sender_id=user_id,
                        text=data["text"]
                    )

                    # Отправляем сообщение всем участникам чата
                    await manager.send_message({
                        "type": "message",
                        "id": message.id,
                        "chat_id": message.chat_id,
                        "sender_id": message.sender_id,
                        "text": message.text,
                        "timestamp": message.timestamp.isoformat(),
                        "is_read": message.is_read
                    }, message.chat_id)

                elif data["type"] == "read_receipt":
                    # Обновляем статус прочтения
                    message = await self.message_repository.get_by_id(data["message_id"])
                    if message:
                        await self.message_repository.mark_as_read(message.id)
                        await manager.send_read_receipt(
                            message.id,
                            message.chat_id,
                            user_id
                        )

        except WebSocketDisconnect:
            await manager.disconnect(user_id) 
