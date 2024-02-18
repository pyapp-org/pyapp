"""
Compatibility Utils
~~~~~~~~~~~~~~~~~~~

Utils for managing deprecation of methods and tools

"""

import functools
import inspect
import warnings
from typing import Type


def deprecated(message: str, category: Type[Warning] = DeprecationWarning):
    """
    Decorator for marking classes/functions as being deprecated and are to be removed in the future.

    :param message: Message provided.
    :param category: Category of warning.

    """

    def decorator(obj):
        if inspect.isclass(obj):
            old_init = obj.__init__

            @functools.wraps(old_init)
            def init_wrapper(*args, **kwargs):
                warnings.warn(
                    f"{obj.__name__} is deprecated and scheduled for removal. {message}",
                    category=category,
                    stacklevel=2,
                )
                return old_init(*args, **kwargs)

            obj.__init__ = init_wrapper
            return obj

        @functools.wraps(obj)
        def func_wrapper(*args, **kwargs):
            warnings.warn(
                "{obj.__name__} is deprecated and scheduled for removal. {message}",
                category=category,
                stacklevel=2,
            )
            return obj(*args, **kwargs)

        return func_wrapper

    return decorator
