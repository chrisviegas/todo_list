from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.todo_list.settings import Settings

engine = create_async_engine(
    Settings().DATABASE_URL,  # pyright: ignore[reportCallIssue]
    max_overflow=10,
    pool_size=5,
    pool_recycle=200,
)


async def get_session():  # pragma: nocover
    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s
