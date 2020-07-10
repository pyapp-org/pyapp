from argparse import FileType
from enum import Enum
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


class Colour(Enum):
    Red = "red"
    Green = "green"


def func_backwards_compatible_1(opts):
    pass


def func_backwards_compatible_2(opts):
    pass


@expected_args()
def func_sample_01():
    pass


@expected_args(mock.call("arg1", type=str, metavar="ARG1", dest="arg1"))
def func_sample_02(arg1: str):
    pass


@expected_args(mock.call("arg1", type=str, metavar="ARG1", dest="arg1", nargs="+"))
def func_sample_03(arg1: Sequence[str]):
    pass


@expected_args(mock.call("foo", type=int, metavar="FOO", dest="arg1"))
def func_sample_04(arg1: int = Arg(name="foo")):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", type=str, metavar="ARG2", dest="arg2", default="foo"),
)
def func_sample_05(arg1: str, *, arg2: str = "foo"):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", action="store_true", metavar="ARG2", dest="arg2"),
)
def func_sample_06(arg1: str, *, arg2: bool):
    pass


@expected_args(mock.call("arg1", action=KeyValueAction, dest="arg1", nargs="+"),)
def func_sample_07(arg1: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", action=KeyValueAction, dest="arg2"),
)
def func_sample_08(arg1: str, *, arg2: dict):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", type=int, metavar="ARG2", dest="arg2", required=True),
)
def func_sample_09(arg1: str, *, arg2: int):
    pass


@expected_args(
    mock.call("arg1", type=str, metavar="ARG1", dest="arg1"),
    mock.call("--arg2", type=Colour, action=EnumName, dest="arg2", default=Colour.Red),
)
def func_sample_10(arg1: str, *, arg2: Colour = Colour.Red):
    pass


@expected_args(mock.call("arg1", type=FileType("w"), metavar="ARG1", dest="arg1"),)
def func_sample_11(arg1: FileType("w")):
    pass


@pytest.mark.parametrize(
    "handler",
    (
        # func_backwards_compatible_1,
        # func_backwards_compatible_2,
        func_sample_01,
        func_sample_02,
        func_sample_03,
        func_sample_04,
        func_sample_05,
        func_sample_06,
        func_sample_07,
        func_sample_08,
        func_sample_09,
        func_sample_10,
        func_sample_11,
    ),
)
def test_from_parameter(handler):
    mock_parser = mock.Mock()
    CommandProxy(handler, mock_parser)

    assert mock_parser.add_argument.mock_calls == handler.expected
