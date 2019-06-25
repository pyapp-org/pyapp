import mock
import pytest

from io import StringIO
from yarl import URL

from pyapp.conf.loaders import http_loader
from pyapp.exceptions import UnsupportedContentType, InvalidConfiguration


class TestRetrieveFile:
    def test_retrieve_file__ok(self):
        pass


class TestHttpLoader:
    @pytest.fixture
    def target(self):
        return http_loader.HttpLoader.from_url(URL("http://hostname/foo/bar.json"))

    def test_str(self, target: http_loader.HttpLoader):
        assert str(target) == "http://hostname/foo/bar.json"

    def test_close(self, target: http_loader.HttpLoader):
        mock_fp = mock.Mock()

        target._fp = mock_fp
        target.close()

        mock_fp.close.assert_called()

    def test_iter(self, target: http_loader.HttpLoader, monkeypatch):
        retrieve_file_mock = mock.Mock(
            return_value=(StringIO('{"FOO": "bar"}'), "application/json")
        )
        monkeypatch.setattr(http_loader, "retrieve_file", retrieve_file_mock)

        with target:
            actual = list(target)

        assert actual == [("FOO", "bar")]

    def test_iter__io_error(self, target: http_loader.HttpLoader, monkeypatch):
        retrieve_file_mock = mock.Mock(side_effect=IOError)
        monkeypatch.setattr(http_loader, "retrieve_file", retrieve_file_mock)

        with target, pytest.raises(InvalidConfiguration):
            list(target)

    def test_iter__unknown_type(self, target: http_loader.HttpLoader, monkeypatch):
        retrieve_file_mock = mock.Mock(
            return_value=(StringIO('{"FOO": "bar"}'), "application/eek")
        )
        monkeypatch.setattr(http_loader, "retrieve_file", retrieve_file_mock)

        with target, pytest.raises(UnsupportedContentType):
            list(target)

    def test_iter__invalid_json(self, target: http_loader.HttpLoader, monkeypatch):
        retrieve_file_mock = mock.Mock(
            return_value=(StringIO('{"FOO": "bar}'), "application/json")
        )
        monkeypatch.setattr(http_loader, "retrieve_file", retrieve_file_mock)

        with target, pytest.raises(InvalidConfiguration):
            list(target)

    def test_iter__invalid_data(self, target: http_loader.HttpLoader, monkeypatch):
        retrieve_file_mock = mock.Mock(
            return_value=(StringIO('["FOO"]'), "application/json")
        )
        monkeypatch.setattr(http_loader, "retrieve_file", retrieve_file_mock)

        with target, pytest.raises(InvalidConfiguration):
            list(target)
