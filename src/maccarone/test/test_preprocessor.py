import pytest

from textwrap import dedent

from maccarone.preprocessor import (
    PresentPiece,
    MissingPiece,
    raw_source_to_pieces,
    get_last_line,
    raw_pieces_to_tagged_input,
    tagged_output_to_completed_pieces,
)

@pytest.mark.parametrize("input, expected", [
    (
        "",
        [PresentPiece("")],
    ),
    (
        "This is a normal string",
        [PresentPiece("This is a normal string")],
    ),
    (
        "This string has #<<one>> missing piece",
        [
            PresentPiece("This string has "),
            MissingPiece("", "one"),
            PresentPiece(" missing piece"),
        ],
    ),
    (
        "This string has #<<one>> and #<<two>> missing pieces",
        [
            PresentPiece("This string has "),
            MissingPiece("", "one"),
            PresentPiece(" and "),
            MissingPiece("", "two"),
            PresentPiece(" missing pieces"),
        ],
    ),
])
def test_raw_source_to_pieces(input, expected):
    assert list(raw_source_to_pieces(input)) == expected

@pytest.mark.parametrize("text,expected", [
    ("\nThis is line 1.\nThis is line 2.\nThis is line 3.", "This is line 3."),
    ("This is a single line with no newline", "This is a single line with no newline"),
    ("", ""),
    ("Line 1\nLine 2\nLine 3\n", ""),
    ("Line 1\nLine 2\nLine 3\n    ", "    "),
])
def test_get_last_line(text, expected):
    assert get_last_line(text) == expected

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
