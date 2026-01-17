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
