from pathlib import Path

import pytest

from pyapp.conf.loaders import file_loader
from pyapp.exceptions import InvalidConfiguration


class TestFileLoader:
    def test__valid_file(self, fixture_path: Path):
        file = fixture_path / "settings.json"
        target = file_loader.FileLoader(file, "application/json")

        actual = dict(target)

        assert str(target) == f"file://{file}?type=application/json"
        assert actual == {"UPPER_CASE": "foo"}

    def test__missing_file(self, fixture_path: Path):
        file = fixture_path / "missing-file.json"
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"

    def test__invalid_file(self, fixture_path: Path):
        file = fixture_path / "settings-invalid-file.json"
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"

    def test__invalid_container(self, fixture_path: Path):
        file = fixture_path / "settings-invalid-container.json"
        target = file_loader.FileLoader(file, "application/json")

        with pytest.raises(InvalidConfiguration):
            dict(target)

        assert str(target) == f"file://{file}?type=application/json"
