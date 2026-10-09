from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlmodel import select

from db import create_db_and_tables
from routers import todos, user

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(todos.router, prefix="/todos", tags=["todos"])
app.include_router(user.router, prefix="/auth", tags=["auth"])



