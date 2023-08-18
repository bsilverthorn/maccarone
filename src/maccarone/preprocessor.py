import re
import logging

from dataclasses import dataclass
from itertools import chain
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from parsimonious.nodes import (
    Node,
    NodeVisitor,
)
from parsimonious.grammar import Grammar

from maccarone.openai import ChatAPI

logger = logging.getLogger(__name__)

@dataclass
class Piece:
    start: int
    end: int

@dataclass
class PresentPiece(Piece):
    text: str

@dataclass
class MissingPiece(Piece):
    indent: str
    guidance: str
    inlined: Optional[str] = None
    enabled: bool = True

    def get_line_pos(self, raw_source: str) -> Tuple[int, int]:
        start_line = raw_source.count('\n', 0, self.start) + 1
        end_line = raw_source.count('\n', 0, self.end) + 1

        return (start_line, end_line)

    def complete(self, replacement: Optional[str]) -> str:
        (indent, guidance) = (self.indent, self.guidance)

        if "\n" in guidance:
            guidance_lines = "\n"
            guidance_lines += "\n".join(f"{indent}#{line}" for line in guidance.splitlines())
            guidance_lines += f"\n{indent}#"
        else:
            guidance_lines = guidance

        source = f"{indent}#<<{guidance_lines}>>\n"

        if replacement is not None:
            source += indent + indent.join(replacement.splitlines(True))
            source += f"{indent}#<</>>\n"
        elif self.inlined is not None:
            source += self.inlined
            source += f"{indent}#<</>>\n"

        return source

grammar = Grammar(
    r"""
    maccarone = human_source maccarone_chunk*
    maccarone_chunk = snippet human_source?

    snippet = snippet_open (ai_source snippet_close)?
    snippet_open = snippet_open_single / snippet_open_multi
    snippet_open_single = guidance_open guidance_inner ">>" nl
    snippet_open_multi = guidance_open nl guidance_lines guidance_close
    snippet_close = ws "#<</>>" nl

    guidance_open = ws "#<<"
    guidance_close = ws "#>>" nl
    guidance_line = ws "#" guidance_inner nl
    guidance_lines = guidance_line+
    guidance_inner = ~"((?!>>).)*"

    human_source = source_line*
    ai_source = source_line*
    source_line = !(guidance_open / guidance_close / snippet_close) ws ~".*" nl?

    ws = ~"[ \t]*"
    nl = ws ~"[\r\n]"
    """
)

@dataclass
class GuidanceOpen:
    indent: str

@dataclass
class Guidance:
    text: str

@dataclass
class SnippetOpen:
    indent: str
    guidance: str

def find_line_number(text: str, pos: int):
    #<<find the line number of the given char position>>
    return text.count('\n', 0, pos) + 1
    #<</>>

class RawSourceVisitor(NodeVisitor):
    def __init__(self, raw_source: str, block_at_line: Optional[int] = None):
        self._raw_source = raw_source
        self._block_at_line = block_at_line

    def generic_visit(self, node: Node, visited_children: List[Node]):
        return visited_children or node

    def visit_maccarone(self, node: Node, visited_children: list):
        (first_source, chunks) = visited_children

        return [first_source] + list(chain(*chunks))

    def visit_maccarone_chunk(self, node: Node, visited_children: list):
        (snippet, source) = visited_children

        if isinstance(source, list):
            source_list = source
        else:
            source_list = []

        return [snippet] + source_list

    def visit_snippet(self, node: Node, visited_children: list):
        (snippet_open, quantified_source) = visited_children

        if self._block_at_line is None:
            enabled = True
        else:
            start_line = find_line_number(self._raw_source, node.start)
            end_line = find_line_number(self._raw_source, node.end)
            enabled = start_line <= self._block_at_line <= end_line

        if isinstance(quantified_source, list):
            ((source, _),) = quantified_source
        else:
            source = None

        #<<return MissingPiece>>
        return MissingPiece(
            start=node.start,
            end=node.end,
            indent=snippet_open.indent,
            guidance=snippet_open.guidance,
            enabled=enabled,
            inlined=source,
        )
        #<</>>

    def visit_snippet_open(self, node: Node, visited_children: list):
        (single_or_multi,) = visited_children

        return single_or_multi

    def visit_snippet_open_single(self, node: Node, visited_children: list):
        (guidance_open, guidance, _, _) = visited_children

        return SnippetOpen(
            indent=guidance_open.indent,
            guidance=guidance.text,
        )

    def visit_snippet_open_multi(self, node: Node, visited_children: list):
        (guidance_open, _, guidance, _) = visited_children

        return SnippetOpen(
            indent=guidance_open.indent,
            guidance=guidance.text,
        )

    def visit_guidance_open(self, node: Node, visited_children: list):
        (ws, _) = visited_children

        return GuidanceOpen(indent=ws.text)

    def visit_guidance_line(self, node: Node, visited_children: list):
        (_, _, guidance_inner, _) = visited_children

        return guidance_inner

    def visit_guidance_lines(self, node: Node, visited_children: list):
        return Guidance(
            text="\n".join(g.text for g in visited_children)
        )

    def visit_guidance_inner(self, node: Node, visited_children: list):
        return Guidance(text=node.text)

    def visit_human_source(self, node: Node, visited_children: list):
        return PresentPiece(
            start=node.start,
            end=node.end,
            text=node.text,
        )

    def visit_ai_source(self, node: Node, visited_children: list):
        return node.text

def raw_source_to_pieces(input: str, block_at_line: Optional[int] = None) -> List[Piece]:
    tree = grammar.parse(input)
    visitor = RawSourceVisitor(input, block_at_line)
    pieces = visitor.visit(tree)

    return pieces

def raw_pieces_to_tagged_input(raw_pieces: List[Piece]) -> str:
    tag_source = ""
    id = 0

    for piece in raw_pieces:
        if isinstance(piece, PresentPiece):
            tag_source += piece.text
        elif isinstance(piece, MissingPiece):
            if piece.enabled:
                tag_source += f'# <write_this id="{id}">\n{piece.indent}# {piece.guidance}\n{piece.indent}# </>'
                id += 1
            else:
                tag_source += f"{piece.indent}# {piece.guidance}\n"

                if piece.inlined is None:
                    tag_source += f"{piece.indent}# (WIP)"
                else:
                    tag_source += f"{piece.inlined}"
        else:
            raise TypeError("unknown piece type", piece)

    logger.debug("tagged input ↓\n%s", tag_source)

    return tag_source

def tagged_input_to_tagged_output(tagged_input: str, chat_api: ChatAPI) -> str:
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
    tagged_output = chat_api.complete_chat("tagged_input_to_tagged_output", chat_messages)

    logger.debug("tagged output ↓\n%s", tagged_output)

    return tagged_output

def tagged_output_to_completed_pieces(tagged_output: str) -> Dict[int, str]:
    pattern = re.compile(r'<completed id="(?P<id>\d+)">\n(?P<content>.+?)</(completed)?>', re.DOTALL)
    matches = pattern.finditer(tagged_output)
    completed = {int(m.group("id")): m.group("content") for m in matches}

    return completed

def pieces_to_final_source(
        raw_pieces: List[Piece],
        completed_pieces: Dict[int, str],
    ) -> str:
    id = 0
    final_source = ""

    for raw in raw_pieces:
        if isinstance(raw, PresentPiece):
            final_source += raw.text
        elif isinstance(raw, MissingPiece):
            if raw.enabled:
                final_source += raw.complete(completed_pieces[id])
                id += 1
            else:
                final_source += raw.complete(None)
        else:
            raise TypeError("unknown piece type", raw)

    logger.debug("final source ↓\n%s", final_source)

    return final_source

def preprocess_maccarone(
        raw_source: str,
        chat_api: ChatAPI,
        block_at_line: Optional[int] = None,
    ) -> str:
    raw_pieces = raw_source_to_pieces(raw_source, block_at_line)
    tagged_input = raw_pieces_to_tagged_input(raw_pieces)
    tagged_output = tagged_input_to_tagged_output(tagged_input, chat_api)
    completed_pieces = tagged_output_to_completed_pieces(tagged_output)
    final_source = pieces_to_final_source(
        raw_pieces,
        completed_pieces,
    )

    return final_source
