from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.fastapi_zero.database import get_session
from src.fastapi_zero.models import User
from src.fastapi_zero.schemas import Token
from src.fastapi_zero.security import create_access_token, verify_password

router = APIRouter(tags=["auth"], prefix="/auth")

SessionDep = Annotated[Session, Depends(get_session)]
OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2FormDep,
    session: SessionDep,
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorret email or password",
        )

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "Bearer"}
