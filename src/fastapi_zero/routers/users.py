from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.fastapi_zero.database import get_session
from src.fastapi_zero.models import User
from src.fastapi_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from src.fastapi_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(tags=["users"], prefix="/users")

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: SessionDep):

    db_user = await session.scalar(
        select(User).where(User.email == user.email)
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Already exists a user with this email.",
        )
    db_user = User(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
async def get_all_users(
    session: SessionDep,
    current_user: CurrentUserDep,
    filter_users: Annotated[FilterPage, Query()],
):
    users = await session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    )
    return {"users": users}


@router.get("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user(user_id: int, session: SessionDep):
    user_db = await session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found.",
        )

    return user_db


@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions."
        )

    try:
        current_user.email = user.email
        current_user.name = user.name
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Already exists a user with this email.",
        )


@router.delete("/{user_id}", status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions."
        )

    await session.delete(current_user)
    await session.commit()
    return {"message": "User deleted."}
