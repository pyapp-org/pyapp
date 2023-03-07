from pathlib import Path
from unittest import mock

import pytest
from pyapp.utils import inspect

import tests


@pytest.mark.parametrize(
    "path, expected",
    (
        (Path(inspect.__file__), "pyapp"),
        (Path(__file__), "tests"),
        (Path(__file__).parent, "tests"),
    ),
)
def test_find_root_folder__in_package(path: Path, expected: str):
    actual = inspect.find_root_folder(path)
    assert actual.name == expected


@pytest.mark.parametrize(
    "path", (Path(__file__) / "../fixtures", Path(__file__) / "../fixtures/my_file.py")
)
def test_find_root_folder__outside_package(path):
    with pytest.raises(ValueError, match="File not part of a package"):
        inspect.find_root_folder(path)


def test_import_root_module__current_module():
    actual = inspect.import_root_module(1)

    assert actual is tests


def test_import_root_module__single_file(monkeypatch):
    stack_mock = mock.Mock()
    stack_mock.frame.f_globals = {"__name__": "__main__", "__file__": "/foo/bar.py"}
    monkeypatch.setattr(
        inspect.inspect, "stack", mock.Mock(return_value=[None, None, stack_mock])
    )
    monkeypatch.setattr(
        inspect, "find_root_folder", mock.Mock(side_effect=ValueError("EEK!"))
    )

    actual = inspect.import_root_module()

    assert actual == __import__("__main__")


def test_import_root_module__unknown(monkeypatch):
    stack_mock = mock.Mock()
    stack_mock.frame.f_globals = {"__name__": "foo", "__file__": "/foo/bar.py"}
    monkeypatch.setattr(inspect.inspect, "stack", mock.Mock(return_value=[stack_mock]))
    monkeypatch.setattr(
        inspect, "find_root_folder", mock.Mock(side_effect=ValueError("EEK!"))
    )

    with pytest.raises(RuntimeError, match="Unable to determine root module"):
        inspect.import_root_module(-1)
