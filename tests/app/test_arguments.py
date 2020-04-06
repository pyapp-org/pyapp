import argparse

import mock
import pytest

import tests.sample_app
from pyapp.app import arguments


class TestHandlerProxy:
    def test_basic_usage(self):
        def sample_handler(_):
            return 1

        mock_parser = mock.Mock()

        target = arguments.CommandProxy(sample_handler, mock_parser)

        assert sample_handler is target.handler
        assert sample_handler.__doc__ == target.__doc__
        assert sample_handler.__name__ == target.__name__
        assert sample_handler.__module__ == target.__module__
        assert target(None) == 1

    def test_with_arguments(self):
        @arguments.argument("--foo", dest="foo", help_text="Foo option")
        @arguments.argument("--bar", dest="bar", help_text="Bar option")
        def sample_handler():
            pass

        mock_parser = mock.Mock()
        arguments.CommandProxy(sample_handler, mock_parser)

        assert mock_parser.add_argument.call_count == 2


class TestCommandGroup:
    @pytest.fixture
    def target(self):
        return arguments.CommandGroup(argparse.ArgumentParser("test"))

    @pytest.mark.parametrize(
        "prefix, expected", ((None, ":handler:"), ("foo", ":handler:foo"))
    )
    def test_handler_dest(self, prefix, expected):
        target = arguments.CommandGroup(argparse.ArgumentParser("test"), _prefix=prefix)

        assert target.handler_dest == expected

    def test_create_command_group(self, target: arguments.CommandGroup):
        actual = target.create_command_group("foo", help_text="bar", aliases=("f",))

        assert isinstance(actual, arguments.CommandGroup)
        assert actual.parser.prog == "test foo"
        assert "foo" in target._handlers
        assert "f" in target._handlers

    def test_create_command_group__nested(self, target: arguments.CommandGroup):
        group = target.create_command_group("foo")
        actual = group.create_command_group("bar")

        assert actual.handler_dest == ":handler:foo:bar"

    def test_default(self, target: arguments.CommandGroup):
        @target.default
        def my_default(args):
            return 13

        actual = target.dispatch_handler(argparse.Namespace())

        assert actual == 13

    def test_dispatch_handler__known_command(self, target: arguments.CommandGroup):
        @target.command
        def known(args) -> int:
            return 42

        actual = target.dispatch_handler(argparse.Namespace(**{":handler:": "known"}))

        assert actual == 42

    def test_dispatch_handler__unknown_command(self, target: arguments.CommandGroup):
        @target.command
        def known(args) -> int:
            return 42

        actual = target.dispatch_handler(argparse.Namespace(**{":handler:": "unknown"}))

        assert actual == 1

    def test_dispatch_handler__nested_command(self, target: arguments.CommandGroup):
        group = target.create_command_group("foo")

        @group.command
        def known(args) -> int:
            return 24

        actual = target.dispatch_handler(
            argparse.Namespace(**{":handler:foo": "known", ":handler:": "foo"})
        )

        assert actual == 24

    def test_dispatch_handler__with_alias(self, target: arguments.CommandGroup):
        group = target.create_command_group("foo")

        @group.command(aliases=("k", "kwn"))
        def known(args) -> int:
            return 42

        actual = target.dispatch_handler(
            argparse.Namespace(**{":handler:foo": "kwn", ":handler:": "foo"})
        )

        assert actual == 42
