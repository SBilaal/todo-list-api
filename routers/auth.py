from contextlib import asynccontextmanager

from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import or_, select

from db import SessionDep, User, UserCreate, UserResponse, create_db_and_tables
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    session: SessionDep,
    user_create: UserCreate
):
    existing_user = session.exec(select(User).where(or_(User.username == user_create.username, User.email == user_create.email))).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    if not existing_user:
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=password_hash.hash(user_create.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user