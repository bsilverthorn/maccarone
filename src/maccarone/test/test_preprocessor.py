import pytest

from maccarone.preprocessor import (
    PieceType,
    yield_source_pieces,
    get_last_line,
)

@pytest.mark.parametrize("input, expected", [
    (
        "",
        [(PieceType.PRESENT, "")],
    ),
    (
        "This is a normal string",
        [(PieceType.PRESENT, "This is a normal string")],
    ),
    (
        "This string has #<<one>> missing piece",
        [
            (PieceType.PRESENT, "This string has "),
            (PieceType.MISSING, "one"),
            (PieceType.PRESENT, " missing piece"),
        ],
    ),
    (
        "This string has #<<one>> and #<<two>> missing pieces",
        [
            (PieceType.PRESENT, "This string has "),
            (PieceType.MISSING, "one"),
            (PieceType.PRESENT, " and "),
            (PieceType.MISSING, "two"),
            (PieceType.PRESENT, " missing pieces"),
        ],
    ),
])
def test_extract_missing_pieces(input, expected):
    assert list(yield_source_pieces(input)) == expected

@pytest.mark.parametrize("text,expected", [
    ("\nThis is line 1.\nThis is line 2.\nThis is line 3.", "This is line 3."),
    ("This is a single line with no newline", "This is a single line with no newline"),
    ("", ""),
    ("Line 1\nLine 2\nLine 3\n", ""),
    ("Line 1\nLine 2\nLine 3\n    ", "    "),
])
def test_get_last_line(text, expected):
    assert get_last_line(text) == expected
