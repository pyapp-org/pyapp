import contextlib
import ssl
import tempfile

from typing import TextIO, Tuple
from urllib.error import ContentTooShortError
from urllib.request import urlopen
from yarl import URL

from pyapp.exceptions import InvalidConfiguration
from .base import Loader
from .content_types import registry, content_type_from_url


def retrieve_file(url: URL) -> Tuple[TextIO, str]:
    """
    Fetch a file from a URL (handling SSL).

    This is based off `urllib.request.urlretrieve`.
    """
    if url.scheme not in ("http", "https"):
        raise InvalidConfiguration("Illegal scheme.")

    context = ssl.SSLContext if url.scheme == "https" else None

    with contextlib.closing(
        urlopen(url, context=context)  # nosec - There is a check above for SSL
    ) as fp:
        bs = 1024 * 8
        size = -1
        read = 0

        headers = fp.info()
        if "content-length" in headers:
            size = int(headers["Content-Length"])

        if "content-type" in headers:
            content_type = headers["Content-Type"]
        else:
            content_type = content_type_from_url(url)

        tfp = tempfile.TemporaryFile()
        while True:
            block = fp.read(bs)
            if not block:
                break
            read += len(block)
            tfp.write(block)

    if size >= 0 and read < size:
        raise ContentTooShortError(
            f"retrieval incomplete: got only {read} out of {size} bytes", headers
        )

    return tfp, content_type


class HttpLoader(Loader):
    """
    Load settings from a file.

    Usage::

        >>> loader = HttpLoader(URL("https://hostname/path/to/settings.json"))
        >>> settings = dict(loader)

    """

    scheme = ("http", "https")

    @classmethod
    def from_url(cls, url: URL) -> Loader:
        """
        Create an instance of :class:`HttpLoader` from :class:`urllib.parse.ParseResult`.
        """
        return HttpLoader(url)

    def __init__(self, url: URL):
        self.url = url
        self._fp = None
        self.content_type = None

    def __del__(self):
        self.close()

    def __iter__(self):
        try:
            if self._fp is None:
                self._fp, self.content_type = retrieve_file(self.url)

            # Seek to start before parsing
            self._fp.seek(0)
        except IOError as ex:
            raise InvalidConfiguration(f"Unable to load settings: {self}\n{ex}")

        try:
            data = registry.parse_file(self._fp, self.content_type)

        except ValueError as ex:
            raise InvalidConfiguration(f"Unable to parse JSON file: {self}\n{ex}")

        # Check we have a valid container object
        if not isinstance(data, dict):
            raise InvalidConfiguration(
                f"Invalid root object, expected a JSON Object: {self}"
            )

        return ((k, v) for k, v in data.items() if k.isupper())

    def __str__(self):
        return str(self.url)

    def close(self):
        """
        Ensure the file pointer is closed
        """
        if self._fp:
            self._fp.close()
            self._fp = None
