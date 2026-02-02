from http import HTTPStatus

from fastapi import FastAPI

from src.todo_list.routers import auth, todos, users
from src.todo_list.schemas import (
    Message,
)

app = FastAPI(title="Todo List API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {"message": "Hello, World!"}
