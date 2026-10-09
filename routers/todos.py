from fastapi import APIRouter, FastAPI, Request, Response, HTTPException, status, Query
from typing import Annotated
import uuid

from sqlmodel import select

from db import SessionDep, Todo, create_db_and_tables, TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, session: SessionDep):
    todo = Todo(
        title=todo.title,
        description=todo.description,
        is_done=todo.is_done,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.get("", response_model=list[TodoResponse])
def get_todos(
    session: SessionDep,
    is_done: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    
):
    selector = select(Todo)
    if is_done is not None:
        selector = selector.where(Todo.is_done == is_done)
    selector = selector.offset(offset).limit(limit)
    todos = session.exec(selector).all()
    return todos


@router.get("/{id}", response_model=TodoResponse)
def get_todo(session: SessionDep, id: uuid.UUID):
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail={"message": "ID can't be found"})
    return todo


@router.put("/{id}", response_model=TodoResponse)
def replace_todo(id: uuid.UUID, todo: TodoCreate, session: SessionDep):
    todo_item = session.get(Todo, id)

    if todo_item is None:
        raise HTTPException(status_code=404, detail={"message": "ID can't be found"})
    todo_data = todo.model_dump()
    todo_item.sqlmodel_update(todo_data)
    session.add(todo_item)
    session.commit()
    session.refresh(todo_item)
    return todo_item

@router.patch("/{id}", response_model=TodoResponse)
def update_todo(id: uuid.UUID, todo: TodoUpdate, session: SessionDep):
    todo_item = session.get(Todo, id)
    if not todo_item:
        raise HTTPException(status_code=404, detail={"message": "ID can't be found"})
    todo_data_item = todo.model_dump(exclude_unset=True)
    todo_item.sqlmodel_update(todo_data_item)
    session.add(todo_item)
    session.commit()
    session.refresh(todo_item)
    return todo_item
    


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(session: SessionDep, id: uuid.UUID):
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail={"message": "ID can't be found"})
    session.delete(todo)
    session.commit()