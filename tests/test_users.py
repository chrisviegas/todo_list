from http import HTTPStatus

from fastapi.testclient import TestClient

from src.fastapi_zero.models import User
from src.fastapi_zero.schemas import UserPublic


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
            "email": user.email,
            "password": "12345678",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "Already exists a user with this email."
    }


def test_get_all_users(client: TestClient, user: User, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_get_user(client: TestClient, user: User):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "name": user.name,
        "email": user.email,
    }


def test_update_user(client: TestClient, user: User, token):
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
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


def test_exeption_update_user(client: TestClient, other_user: User, token):
    response = client.put(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Gabriel",
            "email": "gabriel@email.com",
            "password": "123",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions."}


def test_integrity_update_user(
    client: TestClient, user: User, token, other_user: User
):
    response = client.put(
        f"users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": other_user.name,
            "email": other_user.email,
            "password": "123456",
        },
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": "Already exists a user with this email."
    }


def test_exeption_get_user(client: TestClient):
    response = client.get("/users/2")

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found."}


def test_delete_user(client: TestClient, user: User, token):
    response = client.delete(
        f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted."}


def test_exeption_delete_user(client: TestClient, other_user: User, token):
    response = client.delete(
        f"/users/{other_user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.is_error
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions."}
