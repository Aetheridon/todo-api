import json
import uuid
import sys

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI()
PATH = "todos.json" # make this universal

class Todo(BaseModel):
    todo: str
    complete_by: str

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
        
        updated_todos = [todo for todo in todos if todo["ID"] != id]
        
        if len(updated_todos) == len(todos):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found")
        
        write_data(updated_todos)

        return status.HTTP_200_OK
    
    except Exception as e:
        print("Got error trying to delete todo from datafile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)