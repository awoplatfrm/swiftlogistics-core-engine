from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///swiftlogistic.db")
ASYNC_ENGINE = create_async_engine(DATABASE_URL, echo=True)

session_local = async_sessionmaker(bind=ASYNC_ENGINE)


class Base(DeclarativeBase, AsyncAttrs):
    pass
