from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.fastapi_zero.app import app
from src.fastapi_zero.database import get_session
from src.fastapi_zero.models import User, table_registry
from src.fastapi_zero.security import get_password_hash


@pytest.fixture
def client(session: Session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as s:
        yield s

    table_registry.metadata.drop_all(engine)
    engine.dispose()


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


@pytest.fixture
def user(session: Session):
    password = "mockmock"
    user = User(
        name="Mock",
        email="mock@example.com",
        password=get_password_hash("mockmock"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Add a attribute to the user object in runtime
    user.clean_password = password  # pyright: ignore[reportAttributeAccessIssue]

    return user


@pytest.fixture
def token(client: TestClient, user: User) -> str:
    response = client.post(
        "/login",
        data={"username": user.email, "password": user.clean_password},  # pyright: ignore[reportAttributeAccessIssue]
    )

    return response.json()["access_token"]
