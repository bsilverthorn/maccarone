import pytest

from textwrap import dedent

from maccarone.preprocessor import (
    PresentPiece,
    MissingPiece,
    find_line_number,
    raw_source_to_pieces,
    raw_pieces_to_tagged_input,
    tagged_output_to_completed_pieces,
)

LB = "<"
RB = ">"
LL = "<<" # hide test content from maccarone itself
RR = ">>"
CLOSE = f"#{LL}/{RR}"

@pytest.mark.parametrize("input, expected", [
    (
        f"""
        this source has
        #{LL}a missing piece{RR}
        above
        """,
        [
            PresentPiece(0, 17, "\nthis source has\n"),
            MissingPiece(17, 38, "", "a missing piece"),
            PresentPiece(38, 44, "above\n"),
        ],
    ),
    (
        f"""
        this source has
        #{LL}a missing piece{RR}
        with inline source
        {CLOSE}
        above
        """,
        [
            PresentPiece(0, 17, "\nthis source has\n"),
            MissingPiece(17, 64, "", "a missing piece", "with inline source\n"),
            PresentPiece(64, 70, "above\n"),
        ],
    ),
    (
        f"""
        this source has
        #{LL}
        # a missing piece
        # with multiline guidance
        #{RR}
        and inline source
        {CLOSE}
        above
        """,
        [
            PresentPiece(0, 17, "\nthis source has\n"),
            MissingPiece(
                17,
                94,
                "",
                " a missing piece\n with multiline guidance",
                "and inline source\n",
            ),
            PresentPiece(94, 100, "above\n"),
        ],
    ),
    (
        f"""
        this source has...*
        #{LL}various special chars, (like this){RR}
        and inline source with more chars _-%$
        {CLOSE}
        `and more!`
        """,
        [
            PresentPiece(0, 21, "\nthis source has...*\n"),
            MissingPiece(
                21,
                107,
                "",
                "various special chars, (like this)",
                "and inline source with more chars _-%$\n",
            ),
            PresentPiece(107, 119, "`and more!`\n"),
        ],
    ),
])
def test_raw_source_to_pieces(input, expected):
    assert list(raw_source_to_pieces(dedent(input))) == expected

@pytest.mark.parametrize("raw_pieces, expected", [
    (
        [
            # using fake start/end positions for convenience
            PresentPiece(0, 0, "\ndef add_two_numbers(x, y):\n    "),
            MissingPiece(0, 0, "    ", "add the args"),
            PresentPiece(0, 0, "\n\n"),
            MissingPiece(0, 0, "", "add two numbers from command line args, using argparse"),
            PresentPiece(0, 0, "\n"),
        ],
        dedent(f"""
        def add_two_numbers(x, y):
            # {LB}write_this id="0"{RB}
            # add the args
            # </>
        
        # {LB}write_this id="1"{RB}
        # add two numbers from command line args, using argparse
        # </>
        """),
    ),
])
def test_raw_source_to_tagged_input(raw_pieces, expected):
    assert raw_pieces_to_tagged_input(raw_pieces) == expected

@pytest.mark.parametrize("tagged, expected", [
    (
        f'{LB}completed id="0"{RB}\ndef add_two_numbers(x, y):\n    return x + y\n</>\n',
        {0: 'def add_two_numbers(x, y):\n    return x + y\n'}
    ),
    (
        f'{LB}completed id="1"{RB}\ndef subtract_two_numbers(x, y):\n    return x - y\n</>\n',
        {1: 'def subtract_two_numbers(x, y):\n    return x - y\n'}
    ),
    (
        f'{LB}completed id="1"{RB}\nfoo\n</>\n{LB}completed id="2"{RB}\ndef multiply_two_numbers(x, y):\n    return x * y\n</>\n',
        {
            1: "foo\n",
            2: 'def multiply_two_numbers(x, y):\n    return x * y\n'
        }
    ),
])
def test_tagged_output_to_completed_pieces(tagged, expected):
    assert tagged_output_to_completed_pieces(tagged) == expected

#<<test find_line_number(text, pos); pos is 0-indexed>>
@pytest.mark.parametrize("text, pos, expected", [
    ("hello\nworld", 0, 1),
    ("hello\nworld", 5, 1),
    ("hello\nworld", 6, 2),
    ("hello\nworld", 11, 2),
    ("\nhello\nworld", 0, 1),
    ("\nhello\nworld", 1, 2),
    ("\nhello\nworld", 6, 2),
    ("\nhello\nworld", 7, 3),
    ("\nhello\nworld", 12, 3),
])
def test_find_line_number(text, pos, expected):
    assert find_line_number(text, pos) == expected
#<</>>
