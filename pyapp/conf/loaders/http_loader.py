from urllib.parse import ParseResult

from pyapp.exceptions import InvalidConfiguration
from .base import Loader
from .content_types import registry


class HttpLoader(Loader):
    """
    Load settings from a file.

    Usage::

        >>> loader = HttpLoader('https://hostname/path/to/settings.json')
        >>> settings = dict(loader)

    """

    scheme = ("http", "https")

    @classmethod
    def from_url(cls, parse_result: ParseResult) -> Loader:
        """
        Create an instance of :class:`HttpLoader` from :class:`urllib.parse.ParseResult`.
        """
        return HttpLoader(parse_result.geturl())

    def __init__(self, url: str):
        self.url = url

    def __iter__(self):
        pass  # TODO: Implement HTTP request

    def __str__(self):
        return self.url
