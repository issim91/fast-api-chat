from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.message import Message

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, chat_id: int, sender_id: int, text: str) -> Message:
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Message:
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_chat_messages(
        self,
        chat_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_as_read(self, message_id: int) -> Message:
        message = await self.get_by_id(message_id)
        if message:
            message.is_read = True
            await self.db.commit()
            await self.db.refresh(message)
        return message 