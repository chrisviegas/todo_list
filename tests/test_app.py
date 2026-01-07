from http import HTTPStatus

from fastapi.testclient import TestClient

from src.fastapi_zero.app import app


def test_root():
    """
    This test have 3 steps (AAA)
    - A: Arrange
    - A: Act       - Execute the thing (the SUI)
    - A: Assert    - Make sure that A is A
    """

    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.json() == {"message": "Hello, World!"}
    assert response.status_code == HTTPStatus.OK
