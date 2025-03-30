import json
import sys

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
PATH = "todos.json" # make this universal

class Todo(BaseModel):
    todo: str
    complete_by: str

class TodoUpdate(BaseModel):
    todo: Optional[str] = None
    complete_by: Optional[str] = None

def read_data():
    try:
        with open(PATH, "r") as f:
            todos = json.load(f)

        return todos

    except Exception as e:
        print("Got error trying to read data: {e}")
        sys.exit()

def write_data(data):
    with open(PATH, "w+") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def view_todos():
    todos = read_data()
    return todos

@app.post("/create-todo")
def create_todo(user_todo: Todo):
    try:
        todos = read_data()

        todos.append({"ID": len(todos) + 1, "todo": user_todo.todo, "complete_by": user_todo.complete_by})
        write_data(todos)

        return status.HTTP_200_OK
    
    except Exception as e: 
        print(f"Got error trying to write to datafile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.post("/delete-todo/{id}")
def delete_todo(id: int):
    try:
        todos = read_data()

        if len(todos) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no todos in datafile!")
        
        updated_todos = [todo for todo in todos if todo["ID"] != id]
        
        if len(updated_todos) == len(todos):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found")
        
        write_data(updated_todos)

        return status.HTTP_200_OK
    
    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Got error trying to delete todo from datafile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.post("/edit-todo/{id}")
def edit_todo(id: int, todo_update: TodoUpdate):
    try:
        todos = read_data()

        if len(todos) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no todos in datafile!")

        todo_found = False

        for todo in todos:
            if todo["ID"] == id: #TODO: fucks up if just 1 item in todos
                if todo_update.todo is not None:
                    todo["todo"] = todo_update.todo

                if todo_update.complete_by is not None:
                    todo["complete_by"] = todo_update.complete_by

                todo_found = True
                break
        
        if not todo_found:
            print("todo not found!")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        if todo_update.todo is None and todo_update.complete_by is None:
            print("no new values supplied to update todo with!")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
        write_data(todos)
        return {"message": f"Todo with ID {id} updated successfully"}
    
    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"got error trying to edit todo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)