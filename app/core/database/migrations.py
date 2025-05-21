from sqlalchemy import text
from app.core.database.connection import engine
from app.models.base import Base
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message
from app.models.group import Group

async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all tables from the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 