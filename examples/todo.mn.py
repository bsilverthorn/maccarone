class Todo:
    #<<description, status (done, not done), id number>>

def load_todos() -> list[Todo]:
    #<<load from ~/.todos.json>>

todos = load_todos()

def save_todos(todos: list[Todo]) -> None:
    #<<save todos>>

def add_todo(description):
    #<<add todo and save>>

def remove_todo(id):
    #<<remove todo and save>>

def print_todos():
    #<<print todos>>

#<<command line interface using argparse>>
