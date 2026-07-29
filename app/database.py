from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings

ASYNC_ENGINE = create_async_engine(settings.DATABASE_URL, echo=True)

session_local = async_sessionmaker(bind=ASYNC_ENGINE)


async def db_conn() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        yield session


class Base(DeclarativeBase, AsyncAttrs):
    pass
