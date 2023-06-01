import re
import logging

from dataclasses import dataclass

from maccarone.openai import complete_chat_with_cache

logger = logging.getLogger(__name__)

class Piece:
    pass

@dataclass
class PresentPiece(Piece):
    text: str

@dataclass
class MissingPiece(Piece):
    indent: str
    guidance: str

def raw_source_to_pieces(input: str) -> list[Piece]:
    missing = re.finditer(r"(\n(?P<il>[ \t]*))?(?P<lm>#<<)(?P<gd>.+?)(?P<rm>>>)", input, re.DOTALL)
    position = 0
    pieces = []

    for piece in missing:
        left = piece.start("lm")

        pieces += [
            PresentPiece(text=input[position:left]),
            MissingPiece(
                indent=piece.group("il") or "",
                guidance=piece.group("gd"),
            ),
        ]

        position = piece.end("rm")

    pieces += [PresentPiece(text=input[position:])]

    return pieces

def raw_pieces_to_tagged_input(raw_pieces: list[Piece]) -> str:
    tag_source = ""
    id = 0

    for piece in raw_pieces:
        match piece:
            case PresentPiece(text):
                tag_source += text
            case MissingPiece(indent, guidance):
                tag_source += f'# <write_this id="{id}">\n{indent}# {guidance}\n{indent}# </>'
                id += 1
            case _:
                raise TypeError("unknown piece type", piece)

    logger.debug("tagged input ↓\n%s", tag_source)

    return tag_source

def tagged_input_to_tagged_output(tagged_input: str) -> str:
    system_prompt = """
You are an expert programmer working on contract. Your client has written a partial program, but left pieces for you to complete. They have marked those with `<write_this>` tags inside Python comments, e.g.:

```
def add_two_numbers(x, y):
    # <write_this id="0">
    # add the two numbers
    # </>

# <write_this id="1">
# add two numbers from command line args, using argparse
# </>
```

You should produce a document that provides a `<completed>` tag for each missing piece, e.g.:

```
<completed id="0">
return x + y
</>
<completed id="1">
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("x", type=int)
parser.add_argument("y", type=int)
args = parser.parse_args()
return add_two_numbers(args.x, args.y)
</>
```

This formatting is very important. The client uses a custom tool to process your work product, and their tool requires this format. Follow this format exactly and do not copy anything outside a `<write_this>` tag.
"""
    chat_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": tagged_input},
    ]
    tagged_output = complete_chat_with_cache(chat_messages)

    logger.debug("tagged output ↓\n%s", tagged_output)

    return tagged_output

def tagged_output_to_completed_pieces(tagged_output: str) -> dict[int, str]:
    pattern = re.compile(r'<completed id="(?P<id>\d+)">\n(?P<content>.+?)</>', re.DOTALL)
    matches = pattern.finditer(tagged_output)
    completed = {int(m.group("id")): m.group("content") for m in matches}

    return completed

def pieces_to_final_source(
        raw_pieces: list[Piece],
        completed_pieces: dict[int, str],
    ) -> str:
    id = 0
    final_source = ""

    for raw in raw_pieces:
        match raw:
            case PresentPiece(text):
                final_source += text
            case MissingPiece(indent):
                completed = completed_pieces[id]
                final_source += indent.join(completed.splitlines(True))
                id += 1
            case _:
                raise TypeError("unknown piece type", raw)

    logger.debug("final source ↓\n%s", final_source)

    return final_source

def preprocess_maccarone(raw_source: str) -> str:
    raw_pieces = raw_source_to_pieces(raw_source)
    tagged_input = raw_pieces_to_tagged_input(raw_pieces)
    tagged_output = tagged_input_to_tagged_output(tagged_input)
    completed_pieces = tagged_output_to_completed_pieces(tagged_output)
    final_source = pieces_to_final_source(raw_pieces, completed_pieces)

    return final_source
