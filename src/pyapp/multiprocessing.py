"""
Multi-processing
~~~~~~~~~~~~~~~~

The ``pyapp.multiprocessing`` package provides an implementation of a multiprocessing
``Pool`` that ensures that settings are configured on each of the worker nodes. This
allows for config factory helpers, dependency injection and feature flags to be
safely used.

A ``pyapp.multiprocessing.Pool`` is a drop in replacement for the stdlib
implementation.

"""

from io import BytesIO
from multiprocessing.pool import Pool as _Pool
from typing import Any, Callable, Sequence

from pyapp.conf import export_settings, restore_settings


def pyapp_initializer(pickled_settings: bytes, initializer, init_args):
    """
    initializer for pyApp that that restores pickled settings
    """
    file = BytesIO(pickled_settings)
    restore_settings(file)
    if initializer:
        initializer(*init_args)


def prepare_settings() -> bytes:
    """
    Generate init args for a worker process initializer
    """
    file = BytesIO()
    export_settings(file)
    return file.getvalue()


class Pool(_Pool):
    """
    Wrapper around multiprocessing pool that ensures each worker has a valid
    settings object initialised.
    """

    def __init__(  # noqa: PLR0913
        self,
        processes: int = None,
        initializer: Callable = None,
        initargs: Sequence[Any] = (),
        maxtasksperchild: int = None,
        context: Any = None,
    ):
        if initializer is not None and not callable(initializer):
            raise TypeError("initializer must be a callable")

        super().__init__(
            processes,
            pyapp_initializer,
            (prepare_settings(), initializer, initargs),
            maxtasksperchild,
            context,
        )

    def __reduce__(self):
        raise NotImplementedError(
            "pool objects cannot be passed between processes or pickled"
        )
