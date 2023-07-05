class Todo:
    #<<description, status (done, not done), id number>>
    def __init__(self, description, status='not done', id=None):
        self.description = description
        self.status = status
        self.id = id if id is not None else uuid.uuid4()
    #<</>>

def load_todos() -> list[Todo]:
    #<<load from ~/.todos.json>>
    import json
    import os
    def load_todos() -> list[Todo]:
        if os.path.exists('~/.todos.json'):
            with open('~/.todos.json', 'r') as f:
                todos = json.load(f)
            return [Todo(**todo) for todo in todos]
        else:
            return []
    #<</>>

todos = load_todos()

def save_todos(todos: list[Todo]) -> None:
    #<<save todos>>
    def save_todos(todos: list[Todo]) -> None:
        with open('~/.todos.json', 'w') as f:
            json.dump([todo.__dict__ for todo in todos], f)
    #<</>>

def add_todo(description):
    #<<add todo and save>>
    def add_todo(description):
        todo = Todo(description)
        todos.append(todo)
        save_todos(todos)
    #<</>>

def remove_todo(id):
    #<<remove todo and save>>
    def remove_todo(id):
        todos = [todo for todo in todos if todo.id != id]
        save_todos(todos)
    #<</>>

def print_todos():
    #<<print todos>>
    def print_todos():
        for todo in todos:
            print(f'{todo.id}: {todo.description} - {todo.status}')
    #<</>>

#<<command line interface using argparse>>
import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add', help='Add a new todo')
    parser.add_argument('--remove', help='Remove a todo by id')
    parser.add_argument('--list', action='store_true', help='List all todos')
    args = parser.parse_args()

    if args.add:
        add_todo(args.add)
    elif args.remove:
        remove_todo(args.remove)
    elif args.list:
        print_todos()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
#<</>>
