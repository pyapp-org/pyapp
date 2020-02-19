"""
File Loader
~~~~~~~~~~~

Loads settings from a file

"""
from pathlib import Path
from typing import Union

from yarl import URL

from pyapp.conf.loaders.base import Loader
from pyapp.conf.loaders.content_types import content_type_from_url
from pyapp.conf.loaders.content_types import registry
from pyapp.exceptions import InvalidConfiguration


class FileLoader(Loader):
    """
    Load settings from a file.

    Usage::

        >>> loader = FileLoader('/path/to/settings.json')
        >>> settings = dict(loader)

    """

    scheme = "file"

    @classmethod
    def from_url(cls, url: URL) -> Loader:
        """
        Create an instance of :class:`FileLoader` from :class:`urllib.parse.ParseResult`.
        """
        content_type = content_type_from_url(url)
        return cls(url.path, content_type)

    def __init__(
        self, path: Union[str, Path], content_type: str, *, encoding: str = "UTF8"
    ):
        """
        :param path: Path to file; can be either absolute or relative to PWD.
        :param content_type: Content type of the file
        :param encoding: Encoding of the file; defaults to UTF-8

        """
        self.path = Path(path)
        self.content_type = content_type
        self.encoding = encoding

    def __iter__(self):
        try:
            with self.path.open(encoding=self.encoding) as fp:
                data = registry.parse_file(fp, self.content_type)

        except IOError as ex:
            raise InvalidConfiguration(f"Unable to load settings: {self}\n{ex}")

        except ValueError as ex:
            raise InvalidConfiguration(f"Unable to parse file: {self}\n{ex}")

        # Check we have a valid container object
        if not isinstance(data, dict):
            raise InvalidConfiguration(
                f"Invalid root object, expected an Object: {self}"
            )

        return ((k, v) for k, v in data.items() if k.isupper())

    def __str__(self):
        return f"file://{self.path.as_posix()}?type={self.content_type}"
