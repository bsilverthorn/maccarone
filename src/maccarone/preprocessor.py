import re
import logging

from enum import (
    Enum,
    auto,
)

from maccarone.openai import complete_chat_with_cache

logger = logging.getLogger(__name__)

def get_main_prompts(input: str) -> tuple[str, str]:
    system_prompt = """
You are an expert programmer working on contract. Your client has written a partial program, but left pieces for you to complete. They have marked those with `<write_this>` tags inside Python comments, e.g.

```
def add_two_numbers(x, y):
    # <write_this id="0">
    #    add the two numbers
    # </>
```

which should result in:

```
<completed id="0">
return x + y
</>
```

This formatting is very important. The client uses a custom tool to process your work product, and their tool requires this format. Follow this format exactly and do not copy anything outside a `<write_this>` tag.
"""
    user_prompt = input

    return (system_prompt, user_prompt)

class PieceType(Enum):
    PRESENT = auto()
    MISSING = auto()

def yield_source_pieces(input: str) -> list[str]:
    missing = re.finditer(r"(?P<lm>#<<)(?P<desc>.+?)(?P<rm>>>)", input, re.DOTALL)
    position = 0

    for piece in missing:
        left = piece.start("lm")

        yield (PieceType.PRESENT, input[position:left])
        yield (PieceType.MISSING, piece.group("desc"))

        position = piece.end("rm")

    yield (PieceType.PRESENT, input[position:])

# split source into pieces
# create tag-formatted source
# generate tag-formatted output
# parse into id-mapped dict
# generate final source

def get_last_line(text: str):
    index = text.rfind('\n')

    if index == -1:
        return text
    else:
        return text[index+1:]

def preprocess_maccarone(in_source: str) -> str:
    (system_prompt, user_prompt) = get_main_prompts(in_source)
    chat_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    completion = complete_chat_with_cache(chat_messages)
    insertions = completion.split("\n----\n")
    out_source = ""

    for (piece_type, piece) in yield_source_pieces(in_source):
        if piece_type == PieceType.MISSING:
            insertion = insertions.pop(0)
            inlines = insertion.splitlines(keepends=True)
            lprefix = get_last_line(out_source)

            logger.debug("lprefix %r", lprefix)

            # add insertion, maintaining indent level
            out_source += inlines[0]

            for inline in inlines[1:]:
                out_source += lprefix + inline
        else:
            out_source += piece

    logger.debug("preprocessor output ↓\n%s", out_source)

    return out_source
