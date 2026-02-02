from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.fastapi_zero.database import get_session
from src.fastapi_zero.models import (
    Todo,
    User,
)
from src.fastapi_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from src.fastapi_zero.security import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema, current_user: CurrentUserDep, session: SessionDep
):
    db_todo = Todo(
        user_id=current_user.id,
        title=todo.title,
        description=todo.description,
        state=todo.state,
    )

    session.add(db_todo)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/", response_model=TodoList)
async def get_all_todos(
    session: SessionDep,
    current_user: CurrentUserDep,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))
    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )
    if todo_filter.state:
        query = query.filter(Todo.state.contains(todo_filter.state))

    todos = await session.scalars(
        query.limit(todo_filter.limit).offset(todo_filter.offset)
    )

    return {"todos": todos.all()}


@router.delete("/{todo_id}", response_model=Message)
async def delete_todo(
    todo_id: int, session: SessionDep, current_user: CurrentUserDep
):
    todo_db = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    )

    if not todo_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found."
        )
    await session.delete(todo_db)
    await session.commit()

    return {"message": "Task has been deleted successfully."}


@router.patch("/{todo_id}", response_model=TodoPublic)
async def update_todo(
    todo_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    todo: TodoUpdate,
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found."
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
