import pytest

from argparse import ArgumentParser, Namespace, ArgumentError

from pyapp.app import argument_actions


class TestKeyValueAction:
    def test_init__default_values(self):
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        assert isinstance(target.default, dict)
        assert target.metavar == "KEY=VALUE"

    @pytest.mark.parametrize(
        "value, expected",
        (
            ("x=y", {"x": "y"}),
            ("x=1", {"x": "1"}),
            ("x=", {"x": ""}),
            ("x=a=b", {"x": "a=b"}),
            (("x=1", "y=2"), {"x": "1", "y": "2"}),
        ),
    )
    def test_call__valid(self, value, expected):
        parser = ArgumentParser()
        namespace = Namespace()
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        target(parser, namespace, value)

        assert namespace.options == expected

    @pytest.mark.parametrize("value", ("", "x"))
    def test_call__invalid(self, value):
        parser = ArgumentParser()
        namespace = Namespace()
        target = argument_actions.KeyValueAction(
            option_strings="--option", dest="options"
        )

        with pytest.raises(ArgumentError):
            target(parser, namespace, value)
