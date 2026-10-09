from typing import Annotated
import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Session, SQLModel, create_engine, select

class TodoBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = Field(default=None, index=True)
    is_done: bool = Field(default=False, index=True)

class TodoCreate(SQLModel):
    title: str
    description: str | None = None
    is_done: bool = False
    
class TodoResponse(TodoBase):
    id: uuid.UUID
    created_at: datetime
    last_modified_at: datetime


class TodoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None

class Todo(TodoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False),
    )
    last_modified_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, onupdate=datetime.now, nullable=False),
    )

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    
class UserCreate(UserBase):
    password: str
    pass

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_modified_at: datetime

class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    hashed_password: str | None = None

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str 
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, nullable=False),
    )
    last_modified_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, onupdate=datetime.now, nullable=False),
    )
    

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connection_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connection_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
