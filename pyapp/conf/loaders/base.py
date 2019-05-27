import abc

from typing import Iterable, Tuple, Any, Union, Sequence
from urllib.parse import ParseResult


class Loader(abc.ABC, Iterable[Tuple[str, Any]]):
    """
    ABC class to define the loader interface.
    """

    scheme: Union[str, Sequence[str]]
    """
    Scheme that this loader provides handling of.
    """

    @classmethod
    @abc.abstractmethod
    def from_url(cls, parse_result: ParseResult) -> "Loader":
        """
        Create an instance of a `Loader` using the results of the parsed file URL.
        """
