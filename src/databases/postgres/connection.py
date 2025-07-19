from fastapi import Depends
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from .config import postgres_config

engine: AsyncEngine = create_async_engine(postgres_config.url)

session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with session_maker() as session:
        yield session
        await session.commit()


session_depends: AsyncSession = Depends(get_session)
