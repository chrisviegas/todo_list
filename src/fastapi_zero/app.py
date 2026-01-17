from http import HTTPStatus

from fastapi import FastAPI

from src.fastapi_zero.routers import auth, users
from src.fastapi_zero.schemas import (
    Message,
)

app = FastAPI(title="CRUD API")

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello, World!"}
