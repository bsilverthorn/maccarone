from maccarone.openai import complete_chat_with_cache

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
```

Write this module with the missing pieces filled in. Write only the Python code. Do not write any other text.
"""
    user_prompt = input

    return (system_prompt, user_prompt)

def preprocess_maccarone(in_source: str) -> str:
    (system_prompt, user_prompt) = get_main_prompts(in_source)
    chat_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    completion = complete_chat_with_cache(chat_messages)

    return completion
