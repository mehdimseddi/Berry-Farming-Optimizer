# backend/db/session.py
from sqlmodel.ext.asyncio.session import AsyncSession
from .engine import engine
from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session