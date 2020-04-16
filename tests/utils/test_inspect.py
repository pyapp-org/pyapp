from pathlib import Path

import pytest
from mock import Mock

import tests
from pyapp.utils import inspect


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


def test_import_root_module__unknown(monkeypatch):
    """
    This test assumes the top of the stack won't resolve to a member of a package.

    This is a safe assumption as the top of the stack will usually be the package.
    """
    monkeypatch.setattr(
        inspect, "find_root_folder", Mock(side_effect=ValueError("EEK!"))
    )
    with pytest.raises(RuntimeError, match="Unable to determine root module"):
        inspect.import_root_module(-1)
