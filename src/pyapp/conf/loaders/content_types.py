"""
Content Type Support
~~~~~~~~~~~~~~~~~~~~

Used by File and HTTP loaders to handle both JSON and YAML content.

"""
import mimetypes
from json import load as json_load
from pathlib import Path
from typing import Any, Callable, Dict, Sequence, TextIO, Union

from yarl import URL

# Supported content types
try:
    from yaml import safe_load as yaml_load
except ImportError:  # pragma: no cover
    yaml_load = None

try:
    from toml import load as toml_load
except ImportError:  # pragma: no cover
    toml_load = None

from pyapp.exceptions import UnsupportedContentType

JSON_MIME_TYPE = "application/json"
TOML_MIME_TYPE = "application/toml"  # Ref: https://toml.io/en/v1.0.0#mime-type
YAML_MIME_TYPE = "application/x-yaml"

# These are content types that are not registered but are in common use.
UNOFFICIAL_CONTENT_TYPES = {
    ".toml": TOML_MIME_TYPE,
    ".yaml": YAML_MIME_TYPE,
    ".yml": YAML_MIME_TYPE,
}


def content_type_from_url(url: URL) -> str:
    """
    Determine a content type from a parse result.
    """
    # Check for an explicit type
    file_type = url.query.get("type")
    if not file_type:
        # Fallback to guessing based off the file name
        file_type, _ = mimetypes.guess_type(url.path, strict=False)
        if not file_type:
            # Try non-official source
            extension = Path(url.path).suffix
            file_type = UNOFFICIAL_CONTENT_TYPES.get(extension)

    return file_type


ContentTypeParser = Callable[[TextIO], Dict[str, Any]]


# TODO: Remove when pylint handles typing.List correctly  pylint: disable=fixme
# pylint: disable=unsupported-assignment-operation,no-member
class ContentTypeParserRegistry(Dict[str, ContentTypeParser]):
    """
    Registry of content type parsers.
    """

    def parse_file(self, fp, content_type: str) -> Dict[str, Any]:
        """
        Parse a file using the specified content type.

        :raises: UnsupportedContentType

        """
        content_parser = self.get(content_type)
        if not content_parser:
            raise UnsupportedContentType(f"No parser for `{content_type}`")

        return content_parser(fp)

    def register(
        self, content_types: Union[str, Sequence[str]], parser: ContentTypeParser
    ) -> None:
        """
        Register a content type parser.
        """
        if isinstance(content_types, str):
            content_types = (content_types,)

        for content_type in content_types:
            self[content_type] = parser


registry = ContentTypeParserRegistry(  # pylint: disable=invalid-name
    {JSON_MIME_TYPE: json_load, TOML_MIME_TYPE: toml_load, YAML_MIME_TYPE: yaml_load}
)
