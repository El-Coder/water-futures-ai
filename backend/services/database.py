from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from config.settings import settings
from models.base import Base
import asyncio

# Only create engine if DATABASE_URL is provided
if settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.DEBUG,
        future=True
    )

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    # No database configured - use mock session
    engine = None
    AsyncSessionLocal = None

async def init_db():
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        print("⚠️  No database configured - skipping DB initialization")

async def get_db():
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        # Return None if no database is configured
        yield None