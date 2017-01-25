from __future__ import unicode_literals

import json

from pyapp.exceptions import InvalidConfiguration


class FileLoader(object):
    """
    Load settings from a file.

    Currently only JSON is supported for settings.

    Usage::

        >>> loader = FileLoader('/path/to/settings.json')
        >>> settings = dict(loader)

    """
    scheme = 'file'

    @classmethod
    def from_url(cls, parse_result):
        """
        Create an instance of :class:`FileLoader` from :class:`urllib.parse.ParseResult`.

        :type parse_result: urllib.parse.ParseResult
        :rtype: FileLoader

        """
        return cls(parse_result.path)

    def __init__(self, path, encoding='UTF8'):
        """
        :param path: Path to file; can be either absolute or relative to PWD.
        :type path: str
        :param encoding: Encoding of the file; defaults to UTF-8
        :type encoding: str

        """
        assert path

        self.path = path
        self.encoding = encoding

    def __iter__(self):
        try:
            with open(self.path) as f:
                data = json.load(f)

        except IOError as ex:
            raise InvalidConfiguration("Unable to load settings: {}\n{}".format(self, ex))

        except ValueError as ex:
            raise InvalidConfiguration("Unable to parse JSON file: {}\n{}".format(self, ex))

        # Check we have a valid container object
        if not isinstance(data, dict):
            raise InvalidConfiguration("Invalid root object, expected a JSON Object: {}".format(self))

        return ((k, v) for k, v in data.items() if k.isupper())

    def __str__(self):
        return "{}://{}".format(self.scheme, self.path)
