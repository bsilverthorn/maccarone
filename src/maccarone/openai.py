import os
import logging

from typing import (
    Callable,
    Iterable,
    cast,
)

import openai

from openai import ChatCompletion

from maccarone.caching import (
    DiskCache,
    CacheKeyMissingError,
)

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE", openai.api_base)

def complete_chat(
        messages: list[dict[str, str]],
        model="gpt-4",
        on_token: Callable[[int], None] = lambda p: None,
    ) -> str:
    helicone_key = os.getenv("HELICONE_API_KEY")

    if helicone_key is None:
        headers = {}
    else:
        headers={"Helicone-Auth": helicone_key}

    responses = cast(
        Iterable[ChatCompletion],
        ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.0,
            headers=headers,
        ),
    )
    completion = ""

    logger.info("completing: %r", messages)

    for (i, partial) in enumerate(responses):
        delta = partial.choices[0].delta

        try:
            completion += str(delta.content)
        except AttributeError as error:
            pass

        on_token(i)

    logger.info("completion: %r", completion)

    return completion

class CachedChatAPI:
    def __init__(self, cache_path: str):
        self.cache = DiskCache(cache_path)

    def complete_chat(
            self,
            chat_name: str,
            messages: list[dict[str, str]],
            model="gpt-4",
        ) -> str:
        try:
            return self.cache.get(chat_name, messages)
        except CacheKeyMissingError:
            completion = complete_chat(messages, model=model)

            self.cache.set(chat_name, messages, completion)

            return completion
