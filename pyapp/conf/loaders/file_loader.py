import json

from pathlib import Path
from typing import Union
from urllib.parse import ParseResult

from pyapp.exceptions import InvalidConfiguration


class FileLoader:
    """
    Load settings from a file.

    Currently only JSON is supported for settings.

    Usage::

        >>> loader = FileLoader('/path/to/settings.json')
        >>> settings = dict(loader)

    """

    scheme = "file"

    @classmethod
    def from_url(cls, parse_result: ParseResult) -> "FileLoader":
        """
        Create an instance of :class:`FileLoader` from :class:`urllib.parse.ParseResult`.
        """
        return cls(parse_result.path)

    def __init__(self, path: Union[str, Path], *, encoding: str = "UTF8"):
        """
        :param path: Path to file; can be either absolute or relative to PWD.
        :param encoding: Encoding of the file; defaults to UTF-8

        """
        self.path = Path(path)
        self.encoding = encoding

    def __iter__(self):
        try:
            with self.path.open(encoding=self.encoding) as f:
                data = json.load(f)

        except IOError as ex:
            raise InvalidConfiguration(f"Unable to load settings: {self}\n{ex}")

        except ValueError as ex:
            raise InvalidConfiguration(f"Unable to parse JSON file: {self}\n{ex}")

        # Check we have a valid container object
        if not isinstance(data, dict):
            raise InvalidConfiguration(
                f"Invalid root object, expected a JSON Object: {self}"
            )

        return ((k, v) for k, v in data.items() if k.isupper())

    def __str__(self):
        return f"{self.scheme}://{self.path.as_posix()}"
