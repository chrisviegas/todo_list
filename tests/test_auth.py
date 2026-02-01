from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from fastapi_zero.schemas import Token
from src.fastapi_zero.models import User


def test_login(client: TestClient, user: User):
    response = client.post(
        "auth/login",
        data={
            "username": user.email,
            "password": user.clean_password,  # pyright: ignore[reportAttributeAccessIssue]
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_exception_login(client: TestClient, user: User):
    response = client.post(
        "auth/login",
        data={
            "username": user.email,
            "password": "wrongpassword",
        },  # try login with wrong password
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorret email or password"}


def test_token_expired_after_time(client: TestClient, user: User):
    with freeze_time("2023-07-14 12:00:00"):
        response = client.post(
            "auth/login",
            data={
                "username": user.email,
                "password": user.clean_password,  # pyright: ignore[reportAttributeAccessIssue]
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 12:31:00"):
        response = client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "password": "wrong",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials."}


def test_refresh_token(client: TestClient, user: User, token: Token):
    response = client.post(
        "/auth/refresh_token", headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"


def test_token_expired_dont_refresh(client: TestClient, user: User):
    with freeze_time("2023-07-14 12:00:00"):
        response = client.post(
            "auth/login",
            data={
                "username": user.email,
                "password": user.clean_password,  # pyright: ignore[reportAttributeAccessIssue]
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 12:31:00"):
        response = client.post(
            "/auth/refresh_token", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials."}
