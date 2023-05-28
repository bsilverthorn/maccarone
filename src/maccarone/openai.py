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
    default as cache,
    CacheKeyMissingError,
)

logger = logging.getLogger(__name__)

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

def complete_chat_with_cache(
        messages: list[dict[str, str]],
        model="gpt-4",
    ) -> str:
    try:
        return cache.get(messages)
    except CacheKeyMissingError:
        completion = complete_chat(messages, model=model)

        cache.set(messages, completion)

        return completion
