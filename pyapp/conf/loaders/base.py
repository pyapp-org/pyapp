"""
Base Loader
~~~~~~~~~~~

ABC for loader implementations.

"""
import abc
from typing import Any
from typing import Iterable
from typing import Sequence
from typing import Tuple
from typing import Union

from yarl import URL


class Loader(abc.ABC, Iterable[Tuple[str, Any]]):
    """
    ABC class to define the loader interface.
    """

    scheme: Union[str, Sequence[str]]
    """
    Scheme that this loader provides handling of.
    """

    def __enter__(self) -> "Loader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    @abc.abstractmethod
    def from_url(cls, url: URL) -> "Loader":
        """
        Create an instance of a `Loader` using the results of the parsed file URL.
        """

    def close(self):
        """
        Called by framework when this loader is no longer required.

        This allows any open handles to be closed or caches to be cleared.
        """
