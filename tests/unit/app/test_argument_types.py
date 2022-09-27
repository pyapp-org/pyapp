from argparse import ArgumentTypeError

import pytest
from pyapp.app import argument_types


class TestRegexType:
    def test_valid_value(self):
        target = argument_types.RegexType(r"[a-z]+")

        actual = target("abc")

        assert actual == "abc"

    @pytest.mark.parametrize("value", ("123", "1abc2"))
    def test_invalid_value(self, value):
        target = argument_types.RegexType(r"[a-z]+")

        with pytest.raises(ArgumentTypeError, match="Value does not match "):
            target(value)

    def test_invalid_value_with_a_custom_message(self):
        target = argument_types.RegexType(r"[a-z]+", message="Value not alpha")

        with pytest.raises(ArgumentTypeError, match="Value not alpha"):
            target("123")
