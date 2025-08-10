import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@host:5432/dbname")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
