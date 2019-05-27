from os import path
import pytest

from pyapp.conf.loaders import file_loader
from pyapp.exceptions import InvalidConfiguration

FIXTURES = path.join(path.dirname(__file__), "fixtures")


class TestFileLoader(object):
    def test__valid_file(self):
        file = path.join(FIXTURES, "settings.json")
        target = file_loader.FileLoader(file, "application/json")

        actual = dict(target)

        assert str(target) == f"file://{file}?type=application/json"
        assert actual == {"UPPER_CASE": "foo"}

    def test__missing_file(self):
        file = path.join(FIXTURES, "missing-file.json")
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"

    def test__invalid_file(self):
        file = path.join(FIXTURES, "settings-invalid-file.json")
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"

    def test__invalid_container(self):
        file = path.join(FIXTURES, "settings-invalid-container.json")
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"
