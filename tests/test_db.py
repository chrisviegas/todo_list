from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.fastapi_zero.models import User


def test_create_user(session: Session, mock_db_time):

    with mock_db_time(model=User) as time:
        new_user = User(
            name="Christian", email="chris@example.com", password="secret"
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(
            select(User).where(User.email == "chris@example.com")
        )

    assert asdict(user) == {  # pyright: ignore[reportArgumentType]
        "id": 1,
        "name": "Christian",
        "email": "chris@example.com",
        "password": "secret",
        "created_at": time,
        "updated_at": time,
    }
