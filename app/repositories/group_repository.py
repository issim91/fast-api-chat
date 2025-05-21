from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.models.group import Group, group_members
from app.models.user import User

class GroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, chat_id: int, name: str, creator_id: int) -> Group:
        group = Group(chat_id=chat_id, name=name, creator_id=creator_id)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_by_id(self, group_id: int) -> Group:
        result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        return result.scalar_one_or_none()

    async def add_member(self, group_id: int, user_id: int) -> Group:
        group = await self.get_by_id(group_id)
        if group:
            # Прямая вставка в таблицу связи
            await self.db.execute(
                insert(group_members).values(
                    group_id=group_id,
                    user_id=user_id
                )
            )
            await self.db.commit()
            await self.db.refresh(group)
        return group

    async def remove_member(self, group_id: int, user_id: int) -> Group:
        group = await self.get_by_id(group_id)
        if group:
            # Прямое удаление из таблицы связи
            await self.db.execute(
                group_members.delete().where(
                    (group_members.c.group_id == group_id) &
                    (group_members.c.user_id == user_id)
                )
            )
            await self.db.commit()
            await self.db.refresh(group)
        return group 
