from http import HTTPStatus

from fastapi.testclient import TestClient

from src.fastapi_zero.models import User
from src.fastapi_zero.schemas import UserPublic


def test_root(client: TestClient):  # Arrange
    """
    This test have 3 steps (AAA)
    - A: Arrange
    - A: Act       - Execute the thing (the SUI)
    - A: Assert    - Make sure that A is A
    """

    # Act
    response = client.get("/")

    # Assert
    assert response.json() == {"message": "Hello, World!"}
    assert response.status_code == HTTPStatus.OK


def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "name": "Christian",
            "email": "christian@email.com",
            "password": "12345678",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "name": "Christian",
        "email": "christian@email.com",
    }


def test_exception_create_user(client: TestClient, user: User):
    response = client.post(
        "/users/",
        json={
            "name": "Christian",
            "email": "mock@example.com",
            "password": "12345678",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "Already exists a user with this email."
    }


def test_get_all_users(client: TestClient):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_get_all_users_with_users(client: TestClient, user: User):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user(client: TestClient, user: User):
    response = client.put(
        "/users/1",
        json={
            "name": "Gabriel",
            "email": "gabriel@email.com",
            "password": "123",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "name": "Gabriel",
        "email": "gabriel@email.com",
    }


def test_exeption_update_user(client: TestClient):
    response = client.put(
        "/users/2",
        json={
            "name": "Gabriel",
            "email": "gabriel@email.com",
            "password": "123",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found."}


def test_integrity_update_user(client: TestClient, user: User):
    client.post(
        "/users",
        json={
            "name": "Gabriel",
            "email": "gabriel@email.com",
            "password": "123",
        },
    )

    response = client.put(
        f"users/{user.id}",
        json={
            "name": "Mock Mockado",
            "email": "gabriel@email.com",
            "password": "123456",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "Already exists a user with this email."
    }


def test_get_user(client: TestClient, user: User):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "name": "Mock",
        "email": "mock@example.com",
    }


def test_exeption_get_user(client: TestClient):
    response = client.get("/users/2")

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found."}


def test_delete_user(client: TestClient, user: User):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted."}


def test_exeption_delete_user(client: TestClient):
    response = client.delete("/users/2")

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found."}
