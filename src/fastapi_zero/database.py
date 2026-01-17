from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.fastapi_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)  # pyright: ignore[reportCallIssue]


def get_session():
    with Session(engine) as s:
        yield s
