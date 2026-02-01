from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.fastapi_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)  # pyright: ignore[reportCallIssue]


async def get_session():  # pragma: nocover
    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s
