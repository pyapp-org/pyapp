from argparse import ArgumentTypeError

import pytest

from pyapp.app import argument_types


class TestRegexType:
    def test_valid_value(self):
        target = argument_types.RegexType(r"[a-z]+")

        actual = target("abc")

        assert actual == "abc"

    def test_invalid_value(self):
        target = argument_types.RegexType(r"[a-z]+")

        with pytest.raises(ArgumentTypeError, match="Value does not match "):
            target("123")

    def test_invalid_value_with_a_custom_message(self):
        target = argument_types.RegexType(r"[a-z]+", message="Value not alpha")

        with pytest.raises(ArgumentTypeError, match="Value not alpha"):
            target("123")
