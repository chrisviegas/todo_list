from http import HTTPStatus

from fastapi.testclient import TestClient

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
