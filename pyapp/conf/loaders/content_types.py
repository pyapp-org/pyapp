import mimetypes

from pathlib import Path
from typing import Dict, Any, Callable, TextIO, Union, Sequence
from yarl import URL

# Supported content types
from json import load as json_load

try:
    from yaml import load as yaml_load
except ImportError:
    yaml_load = None

from pyapp.exceptions import UnsupportedContentType

# These are content types that are not registered but are in common use.
UNOFFICIAL_CONTENT_TYPES = {".yaml": "application/x-yaml", ".yml": "application/x-yaml"}


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


registry = ContentTypeParserRegistry(
    {"application/json": json_load, "application/x-yaml": yaml_load}
)
