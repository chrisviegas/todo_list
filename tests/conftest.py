from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from factory.base import Factory
from factory.faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.fastapi_zero.app import app
from src.fastapi_zero.database import get_session
from src.fastapi_zero.models import User, table_registry
from src.fastapi_zero.security import get_password_hash
from src.fastapi_zero.settings import Settings


@pytest.fixture
def client(session: Session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 13)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time

    event.remove(model, "before_insert", fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = "mockmock"
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Add a attribute to the user object in runtime
    user.clean_password = password  # pyright: ignore[reportAttributeAccessIssue]

    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    password = "mockmock"
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Add a attribute to the user object in runtime
    user.clean_password = password  # pyright: ignore[reportAttributeAccessIssue]

    return user


@pytest.fixture
def token(client: TestClient, user: User) -> str:
    response = client.post(
        "auth/login",
        data={"username": user.email, "password": user.clean_password},  # pyright: ignore[reportAttributeAccessIssue]
    )

    return response.json()["access_token"]


@pytest.fixture
def settings():
    return Settings()  # pyright: ignore[reportCallIssue]


class UserFactory(Factory):
    class Meta:  # pyright: ignore
        model = User

    name = Faker("name", locale="pt_BR")
    email = Faker("email", locale="pt_BR")
    password = Faker("password")
