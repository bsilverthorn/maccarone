import importlib.abc
import importlib.machinery
import os
import sys

from typing import Callable, Iterable, cast

import openai

from openai import ChatCompletion

openai.api_key = os.getenv("OPENAI_API_KEY")

def complete_chat(
        messages: list[dict[str, str]],
        model="gpt-4",
        on_token: Callable[[int], None] = lambda p: None,
    ) -> str:
    responses = cast(
        Iterable[ChatCompletion],
        ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.0,
        ),
    )
    completion = ""

    for (i, partial) in enumerate(responses):
        delta = partial.choices[0].delta

        try:
            completion += str(delta.content)
        except AttributeError as error:
            pass

        on_token(i)

    return completion

class ImportFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        print("find_spec", fullname, path, target)

        if path is None or path == '':
            path = [os.getcwd()]  # top level import 

        for entry in path:
            parts = fullname.split(".")
            basename = parts[-1]
            package_path = parts[1:-1]
            filename = os.path.join(entry, *package_path, basename) + '.mn.py'
            print("trying", filename)
            if not os.path.exists(filename):
                continue

            return importlib.machinery.ModuleSpec(
                fullname,
                ImportLoader(fullname, filename),
                origin=filename,
                is_package=False
            )

        return None  # we don't know how to import this

def get_main_prompts(input: str) -> tuple[str, str]:
    system_prompt = """
You are an expert programmer working on contract. Your client has written a partial program, but left some pieces for you to complete. They have marked those pieces inside `#<<>>`, e.g.,

```
#<<instructions to complete this piece of code>>
```

or

```
#<<
# multi-line instructions
# like this
#>>
```"""
    user_prompt = input

    return (system_prompt, user_prompt)

class ImportLoader(importlib.abc.SourceLoader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def get_filename(self, fullname):
        print("get_filename", fullname)
        return self.path

    def get_data(self, filename):
        with open(self.path, 'r') as file:
            in_source = file.read()

        (system_prompt, user_prompt) = get_main_prompts(in_source)
        chat_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        completion = complete_chat(chat_messages)
        print(completion)

        return completion

sys.meta_path.append(ImportFinder())
