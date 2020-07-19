"""
HTTP Loader
~~~~~~~~~~~

Loads settings from an HTTP endpoint (HTTPS is recommended)

"""
import contextlib
import ssl
import tempfile
from typing import TextIO
from typing import Tuple
from urllib.error import ContentTooShortError
from urllib.request import urlopen

from yarl import URL

from pyapp.conf.loaders.base import Loader
from pyapp.conf.loaders.content_types import content_type_from_url
from pyapp.conf.loaders.content_types import registry
from pyapp.exceptions import InvalidConfiguration


def retrieve_file(url: URL) -> Tuple[TextIO, str]:
    """
    Fetch a file from a URL (handling SSL).

    This is based off `urllib.request.urlretrieve`.

    """
    if url.scheme not in ("http", "https"):
        raise InvalidConfiguration("Illegal scheme.")

    context = ssl.SSLContext() if url.scheme == "https" else None

    with contextlib.closing(
        urlopen(url, context=context)  # nosec - There is a check above for SSL
    ) as response:
        block_size = 1024 * 8
        size = -1
        read = 0

        headers = response.info()
        if "Content-Length" in headers:
            size = int(headers["Content-Length"])

        if "Content-Type" in headers:
            content_type = headers["Content-Type"]
        else:
            content_type = content_type_from_url(url)

        tfp = tempfile.TemporaryFile()
        while True:
            block = response.read(block_size)
            if not block:
                break
            read += len(block)
            tfp.write(block)

        # Seek to start
        tfp.seek(0)

    if size >= 0 and read < size:
        tfp.close()

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
            self._fp, self.content_type = retrieve_file(self.url)
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
