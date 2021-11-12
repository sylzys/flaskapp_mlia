import pytest

from app import allowed_file


@pytest.mark.parametrize(
    "test_input,expected", [("file.csv", True), ("file.pdf", False)]
)
def test_allowed_file(test_input, expected):
    assert allowed_file(test_input) == expected
