from io import StringIO
from urllib.error import ContentTooShortError

import mock
import pytest
from yarl import URL

from pyapp.conf.loaders import http_loader
from pyapp.exceptions import InvalidConfiguration
from pyapp.exceptions import UnsupportedContentType
from tests.mock import ANY_INSTANCE_OF


class TestRetrieveFile:
    def test_retrieve_file__invalid_scheme(self):
        with pytest.raises(InvalidConfiguration):
            http_loader.retrieve_file(URL("ftp://hostname/foo/bar.json"))

    @pytest.mark.parametrize(
        "url, expected",
        (
            (URL("http://hostname/foo/bar.json"), None),
            (
                URL("https://hostname/foo/bar.json"),
                ANY_INSTANCE_OF(http_loader.ssl.SSLContext),
            ),
        ),
    )
    def test_retrieve_file__correct_context(self, monkeypatch, url, expected):
        urlopen_mock = mock.Mock(side_effect=AssertionError)
        monkeypatch.setattr(http_loader, "urlopen", urlopen_mock)

        with pytest.raises(AssertionError):
            http_loader.retrieve_file(url)

        urlopen_mock.assert_called_with(url, context=expected)

    @pytest.mark.parametrize(
        "headers", ({}, {"Content-Length": "6"}, {"Content-Type": "application/json"})
    )
    def test_retrieve_file__ok(self, monkeypatch, headers):
        response_mock = mock.Mock()
        response_mock.info.return_value = headers
        response_mock.read.side_effect = [b"foo", b"bar", None]

        urlopen_mock = mock.Mock(return_value=response_mock)
        monkeypatch.setattr(http_loader, "urlopen", urlopen_mock)

        file, content_type = http_loader.retrieve_file(
            URL("http://hostname/foo/bar.json")
        )

        assert content_type == "application/json"
        assert file.read() == b"foobar"

        file.close()

    def test_retrieve_file__invalid_length(self, monkeypatch):
        response_mock = mock.Mock()
        response_mock.info.return_value = {"Content-Length": "10"}
        response_mock.read.side_effect = [b"foo", b"bar", None]

        urlopen_mock = mock.Mock(return_value=response_mock)
        monkeypatch.setattr(http_loader, "urlopen", urlopen_mock)

        with pytest.raises(ContentTooShortError):
            http_loader.retrieve_file(URL("http://hostname/foo/bar.json"))


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
