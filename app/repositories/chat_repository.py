from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat import Chat, ChatType
from app.models.group import Group

class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str = None, type: ChatType = ChatType.PRIVATE) -> Chat:
        chat = Chat(name=name, type=type)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_by_id(self, chat_id: int) -> Chat:
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def has_access(self, chat_id: int, user_id: int) -> bool:
        chat = await self.get_by_id(chat_id)
        if not chat:
            return False

        if chat.type == ChatType.GROUP:
            # Для группового чата проверяем, является ли пользователь членом группы
            return await self.is_group_member(chat_id, user_id)
        return True  # Для приватного чата всегда разрешаем доступ

    async def is_group_member(self, chat_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Group)
            .where(Group.chat_id == chat_id)
            .join(Group.members)
            .where(Group.members.any(id=user_id))
        )
        return result.scalar_one_or_none() is not None 