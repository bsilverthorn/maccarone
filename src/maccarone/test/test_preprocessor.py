import pytest

from textwrap import dedent

from maccarone.preprocessor import (
    PresentPiece,
    MissingPiece,
    raw_source_to_pieces,
    raw_pieces_to_tagged_input,
    tagged_output_to_completed_pieces,
)

@pytest.mark.parametrize("input, expected", [
    (
        """
        this source has
        #<<a missing piece>>
        above
        """,
        [
            PresentPiece(0, 17, "\nthis source has\n"),
            MissingPiece(17, 38, "", "a missing piece"),
            PresentPiece(38, 44, "above\n"),
        ],
    ),
    (
        """
        this source has
        #<<a missing piece>>
        with inline source
        #<</>>
        above
        """,
        [
            PresentPiece(0, 17, "\nthis source has\n"),
            MissingPiece(17, 64, "", "a missing piece", "with inline source\n"),
            PresentPiece(64, 70, "above\n"),
        ],
    ),
    (
        """
        this source has
        #<<
        # a missing piece
        # with multiline guidance
        #>>
        and inline source
        #<</>>
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
        """
        this source has...*
        #<<various special chars, (like this)>>
        and inline source with more chars _-%$
        #<</>>
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
        dedent("""
        def add_two_numbers(x, y):
            # <write_this id="0">
            # add the args
            # </>
        
        # <write_this id="1">
        # add two numbers from command line args, using argparse
        # </>
        """),
    ),
])
def test_raw_source_to_tagged_input(raw_pieces, expected):
    assert raw_pieces_to_tagged_input(raw_pieces) == expected

@pytest.mark.parametrize("tagged, expected", [
    (
        '<completed id="0">\ndef add_two_numbers(x, y):\n    return x + y\n</>\n',
        {0: 'def add_two_numbers(x, y):\n    return x + y\n'}
    ),
    (
        '<completed id="1">\ndef subtract_two_numbers(x, y):\n    return x - y\n</>\n',
        {1: 'def subtract_two_numbers(x, y):\n    return x - y\n'}
    ),
    (
        '<completed id="1">\nfoo\n</>\n<completed id="2">\ndef multiply_two_numbers(x, y):\n    return x * y\n</>\n',
        {
            1: "foo\n",
            2: 'def multiply_two_numbers(x, y):\n    return x * y\n'
        }
    ),
])
def test_tagged_output_to_completed_pieces(tagged, expected):
    assert tagged_output_to_completed_pieces(tagged) == expected
