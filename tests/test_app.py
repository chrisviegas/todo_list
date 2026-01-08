from http import HTTPStatus

from fastapi.testclient import TestClient


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


def test_get_all_users(client: TestClient):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "name": "Christian",
                "email": "christian@email.com",
            }
        ]
    }


def test_update_user(client: TestClient):
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
    assert response.json() == {
        "detail": "User with id 2 does not exist in the database."
    }


def test_get_user(client: TestClient):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "name": "Gabriel",
        "email": "gabriel@email.com",
    }


def test_exeption_get_user(client: TestClient):
    response = client.get("/users/2")

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User with id 2 does not exist in the database."
    }


def test_delete_user(client: TestClient):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "name": "Gabriel",
        "email": "gabriel@email.com",
    }


def test_exeption_delete_user(client: TestClient):
    response = client.delete("/users/2")

    assert response.is_error
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User with id 2 does not exist in the database."
    }
