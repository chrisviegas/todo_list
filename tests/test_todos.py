from http import HTTPStatus

import factory.fuzzy
import pytest
from factory.base import Factory
from factory.faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.todo_list.models import Todo, TodoState, User
from src.todo_list.schemas import Token


class TodoFactory(Factory):
    class Meta:  # pyright: ignore
        model = Todo

    title = Faker("word")
    description = Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client: TestClient, token: Token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            "/todos/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test todo",
                "description": "Test todo description",
                "state": "draft",
            },
        )

    assert response.json() == {
        "id": 1,
        "title": "Test todo",
        "description": "Test todo description",
        "state": "draft",
        "created_at": time.isoformat(),
        "updated_at": time.isoformat(),
    }


@pytest.mark.asyncio
async def test_create_todo_error(session: AsyncSession, user: User):
    todo = Todo(
        title="Test Todo",
        description="Test Desc",
        state="test",  # pyright: ignore
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))


@pytest.mark.asyncio
async def test_get_all_todos_should_return_5_todos(
    session: AsyncSession, client: TestClient, token: Token, user: User
):
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        "/todos/", headers={"Authorization": f"Bearer {token}"}
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_all_todos_pagination_should_return_2_todos(
    session: AsyncSession, client: TestClient, user: User, token: Token
):
    expected_todos = 2

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        "/todos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_all_todos_filter_title_should_return_5_todos(
    session: AsyncSession, client: TestClient, user: User, token: Token
):
    expected_todos = 5

    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title="Test todo 1")
    )

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        "/todos/?title=Test todo 1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_all_todos_filter_description_should_return_5_todos(
    session: AsyncSession, client: TestClient, user: User, token: Token
):
    expected_todos = 5

    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, description="Test todo 1 and something"
        )
    )

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        "/todos/?description=Test todo",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_all_todos_filter_state_should_return_5_todos(
    session: AsyncSession, client: TestClient, user: User, token: Token
):
    expected_todos = 5

    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state="draft")
    )

    await session.commit()

    response = client.get(
        "/todos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_all_todos_should_return_all_expected_fields(
    session: AsyncSession,
    client: TestClient,
    user: User,
    token: Token,
    mock_db_time,
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.json()["todos"] == [
        {
            "created_at": time.isoformat(),
            "updated_at": time.isoformat(),
            "description": todo.description,
            "id": todo.id,
            "state": todo.state,
            "title": todo.title,
        }
    ]


def test_delete_error(client: TestClient, token: Token):
    response = client.delete(
        "/todos/10", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_delete_todo(
    client: TestClient, token: Token, user: User, session: AsyncSession
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f"/todos/{todo.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "message": "Task has been deleted successfully."
    }


@pytest.mark.asyncio
async def test_delete_other_user_todo(
    client: TestClient,
    token: Token,
    other_user: User,
    session: AsyncSession,
):
    todo_other_user = TodoFactory(user_id=other_user.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f"/todos/{todo_other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_update_todo_error(client: TestClient, token: Token):
    response = client.patch(
        "/todos/10", json={}, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_update_todo(
    client: TestClient, token: Token, user: User, session: AsyncSession
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f"/todos/{todo.id}",
        json={"title": "Test title"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "Test title"
