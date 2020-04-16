from urllib.parse import urlparse

import mock
import pytest
from yarl import URL

from pyapp.conf.loaders import content_types


@pytest.mark.parametrize(
    "url, expected",
    (
        ("http://myhost/path/to/my/file.json", "application/json"),
        ("http://myhost/path/to/my/file?type=application/json", "application/json"),
        ("http://myhost/path/to/my/file.yaml", "application/x-yaml"),
        ("file:///path/to/my/file.yml", "application/x-yaml"),
        ("file:///path/to/my/file.txt", "text/plain"),
    ),
)
def test_content_type_from_url__known_types(url: str, expected: str):
    actual = content_types.content_type_from_url(URL(url))

    assert actual == expected


class TestContentTypeParserRegistry:
    def test_parse__known_type(self):
        text_parser = mock.Mock(return_value="foo")

        target = content_types.ContentTypeParserRegistry({"text/plain": text_parser})

        actual = target.parse_file("abc", "text/plain")

        text_parser.assert_called_with("abc")
        assert actual == "foo"

    def test_parse__unknown_type(self):
        text_parser = mock.Mock(return_value="foo")

        target = content_types.ContentTypeParserRegistry({"text/plain": text_parser})

        with pytest.raises(content_types.UnsupportedContentType):
            target.parse_file("abc", "application/json")

    def test_register__single(self):
        target = content_types.ContentTypeParserRegistry()

        target.register("text/plain", content_types.json_load)

        assert len(target) == 1
        assert "text/plain" in target
        assert target["text/plain"] is content_types.json_load

    def test_register__multiple(self):
        target = content_types.ContentTypeParserRegistry()

        target.register(("text/plain", "application/json"), content_types.json_load)

        assert len(target) == 2
        assert "text/plain" in target
        assert "application/json" in target
        assert target["text/plain"] is content_types.json_load
        assert target["application/json"] is content_types.json_load
