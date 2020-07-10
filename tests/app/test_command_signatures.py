from enum import Enum
from enum import IntEnum
from typing import Sequence
from unittest import mock

import pytest

from pyapp.app import KeyValueAction
from pyapp.app.argument_actions import EnumName
from pyapp.app.arguments import Arg
from pyapp.app.arguments import CommandProxy


def expected_args(*args):
    """
    Helper for applying expected add_argment calls to test functions
    """

    def _wrapper(func):
        func.expected = list(args)
        return func

    return _wrapper


class Colour:
    Red = "red"
    Green = "green"


def func_backwards_compatible_1(opts):
    pass


def func_backwards_compatible_2(opts):
    pass


@expected_args()
def func_sample_1():
    pass


@expected_args(mock.call("arg1", type=str, metavar="ARG1", dest="arg1"))
def func_sample_2(arg1: str):
    pass


@expected_args(mock.call("arg1", type=str, metavar="ARG1", dest="arg1", nargs="+"))
def func_sample_3(arg1: Sequence[str]):
    pass


@expected_args(mock.call("foo", type=int, metavar="FOO", dest="arg1"))
def func_sample_4(arg1: int = Arg(name="foo")):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", type=str, metavar="ARG2", dest="arg2", default="foo"),
)
def func_sample_5(arg1: str, *, arg2: str = "foo"):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", action="store_true", metavar="ARG2", dest="arg2"),
)
def func_sample_6(arg1: str, *, arg2: bool):
    pass


@expected_args(mock.call("arg1", action=KeyValueAction, dest="arg1", nargs="+"),)
def func_sample_7(arg1: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", action=KeyValueAction, dest="arg2"),
)
def func_sample_8(arg1: str, *, arg2: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", type=Colour, action=EnumName, dest="arg2", default=Colour.Red),
)
def func_sample_9(arg1: str, *, arg2: Colour = Colour.Red):
    pass


@pytest.mark.parametrize(
    "handler",
    (
        # func_backwards_compatible_1,
        # func_backwards_compatible_2,
        func_sample_1,
        func_sample_2,
        func_sample_3,
        func_sample_4,
        func_sample_5,
        func_sample_6,
        func_sample_7,
        func_sample_8,
        func_sample_9,
    ),
)
def test_from_parameter(handler):
    mock_parser = mock.Mock()
    CommandProxy(handler, mock_parser)

    assert mock_parser.add_argument.mock_calls == handler.expected
