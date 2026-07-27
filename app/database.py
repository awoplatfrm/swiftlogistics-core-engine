from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///swiftlogistic.db")
ASYNC_ENGINE = create_async_engine(DATABASE_URL, echo=True)

session_local = async_sessionmaker(bind=ASYNC_ENGINE)


async def db_conn() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        yield session


class Base(DeclarativeBase, AsyncAttrs):
    pass
