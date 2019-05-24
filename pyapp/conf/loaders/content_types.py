import json
import mimetypes

from typing import Dict, Any, Callable, TextIO, Union, Sequence
from urllib.parse import ParseResult, parse_qs

from pyapp.exceptions import UnsupportedContentType


def content_type_from_url(parse_result: ParseResult) -> str:
    """
    Determine a content type from a parse result.
    """
    # Check for an explicit type
    file_type = parse_qs(parse_result.query).get("type")
    if not file_type:
        # Fallback to guessing based off the file name
        file_type, _ = mimetypes.guess_type(parse_result.path)

    return file_type


ContentTypeParser = Callable[[TextIO], Dict[str, Any]]


class ContentTypeParserRegistry:
    """
    Registry of content type parsers.
    """

    def __init__(self):
        self.content_parsers: Dict[str, ContentTypeParser] = {
            "application/json": json.load
        }

    def parse_file(self, fp, content_type: str) -> Dict[str, Any]:
        """
        Parse a file using the specified content type.

        :raises: UnsupportedContentType

        """
        content_parser = self.content_parsers.get(content_type)
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
            self.content_parsers[content_type] = parser


registry = ContentTypeParserRegistry()
