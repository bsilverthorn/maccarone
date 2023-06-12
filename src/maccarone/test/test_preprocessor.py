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
            PresentPiece("\nthis source has\n"),
            MissingPiece("", "a missing piece"),
            PresentPiece("above\n"),
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
            PresentPiece("\nthis source has\n"),
            MissingPiece("", "a missing piece", "with inline source\n"),
            PresentPiece("above\n"),
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
            PresentPiece("\nthis source has\n"),
            MissingPiece(
                "",
                " a missing piece\n with multiline guidance",
                "and inline source\n",
            ),
            PresentPiece("above\n"),
        ],
    ),
])
def test_raw_source_to_pieces(input, expected):
    assert list(raw_source_to_pieces(dedent(input))) == expected

@pytest.mark.parametrize("raw_pieces, expected", [
    (
        [
            PresentPiece("\ndef add_two_numbers(x, y):\n    "),
            MissingPiece("    ", "add the args"),
            PresentPiece("\n\n"),
            MissingPiece("", "add two numbers from command line args, using argparse"),
            PresentPiece("\n"),
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
