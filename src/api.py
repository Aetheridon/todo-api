import json
import datetime
import logging
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

PATH = "todos.json"

class Todo(BaseModel):
    todo: str
    complete_by: datetime.datetime

class TodoUpdate(BaseModel):
    todo: Optional[str] = None
    complete_by: Optional[datetime.datetime] = None

def check_date(complete_by):
    if complete_by.date() < datetime.date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"date {complete_by} has passed, you may only use today's date or a date in the future")

def check_todo_file(todos, id):
    if not todos or id not in todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"todo with ID {id} does not exist.")

def read_data():
    try:
        with open(PATH, "r") as f:
            todos = json.load(f)
        return todos
    except FileNotFoundError:
        logging.error(f"File at path {PATH} cannot be found", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JSON file for todos not found")
    except Exception as e:
        logging.error(f"Received error when trying to read data from {PATH}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Got error trying to read data from JSON file!")
    
def write_data(data):
    try:
        with open(PATH, "w+") as f:
            json.dump(data, f, indent=4, default=str)
    except FileNotFoundError:
        logging.error(f"File at path {PATH} cannot be found", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JSON file for todos not found")
    except Exception as e:
        logging.error(f"Received error when trying to read data from {PATH}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Got error trying to write data to JSON file!")

@app.get("/")
def view_todos():
    todos = read_data()
    return todos

@app.post("/create-todo")
def create_todo(user_todo: Todo):
    try:
        check_date(complete_by=user_todo.complete_by)
        todos = read_data()
        
        new_id = str(uuid.uuid4())
        while new_id in todos:
            new_id = str(uuid.uuid4())
        todos[new_id] = {"todo": user_todo.todo, "complete_by": user_todo.complete_by}
        write_data(todos)
        return status.HTTP_200_OK
    
    except Exception as e:
        logging.error(f"Received error when trying to create todo: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Got error trying to create todo")
    
@app.post("/delete-todo/{id}")
def delete_todo(id: str):
    try:
        todos = read_data()
        check_todo_file(todos=todos, id=id)
        
        del todos[id]
        write_data(todos)

        return status.HTTP_200_OK
    
    except HTTPException as e:
            raise e
    except Exception as e:
        logging.error(f"Received error when trying to delete todo: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Got error trying to delete todo")
    
@app.post("/edit-todo/{id}")
def edit_todo(id: str, todo_update: TodoUpdate):
    try:
        todos = read_data()
        check_todo_file(todos=todos, id=id)
        check_date(complete_by=todo_update.complete_by)
        
        if todo_update.todo is None and todo_update.complete_by is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please supply a new value to update the todo")
        if todo_update.todo is not None:
            todos[id]["todo"] = todo_update.todo
        if todo_update.complete_by is not None:
            todos[id]["complete_by"] = todo_update.complete_by

        write_data(todos)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Received error when trying to edit todo: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Got error trying to edit todo")
    