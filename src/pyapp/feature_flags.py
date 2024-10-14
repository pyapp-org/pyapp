"""
Feature Flags
~~~~~~~~~~~~~

Runtime configurable feature flags.

Define flags in code either in a code block:

.. code-block:: python

    if feature_flags.get("MY-FLAG"):
        pass

Or as an A/B switch:

.. code-block:: python

    instance = feature_flags.a_or_b("MY-FLAG", option_a="foo", option_b="bar")

.. tip:: ``option_a`` and ``option_b`` parameters can also be callables.

Or by using as a decorator:

.. code-block:: python

    @feature_flags.if_enabled("MY-FLAG", default=True)
    def my_feature(arg):
        pass


Define flags in the applications ``default_settings``:

.. code-block:: python

    FEATURE_FLAGS = {
        "MY-FLAG": True,
        "OTHER-FLAG": False,
    }

The flag can then be enabled/disabled in the environment::

    PYAPP_FLAG_MY_FLAG = yes
    PYAPP_FLAG_OTHER_FLAG = off

.. note:: The flag name is translated into upper-case with underscores

Or from the command line::

    my_app --enable-flag MY-FLAG --disable-flag OTHER-FLAG

"""

import logging
from collections.abc import Callable
from functools import wraps
from os import getenv
from typing import Any, TypeVar

from typing_extensions import Self

from pyapp.conf import settings
from pyapp.utils import text_to_bool

LOGGER = logging.getLogger(__name__)
ENV_TRANSLATE = str.maketrans(
    " -abcdefghijklmnopqrstuvwxyz", "__ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
_F = TypeVar("_F", bound=Callable[..., Any])


class ModifyFeatureFlagsContext:
    """
    Context object used to make temporary modifications to feature flags.

    The main use-case for this feature is within test cases.

    Feature flags can be changed and when the context is exited the
    changes are reverted.

    Example::

        >>> # Directly add settings (you shouldn't normally do this!)
        >>> DEFAULT.set("my-flag", False)
        >>> # Make some changes
        >>> with DEFAULT.modify() as patch:
        ...     # Change state of a flag
        ...     patch["my-flag"] = True
        ...     assert get("my-flag") is True
        >>> # Compare with initial state
        >>> assert get("my-flag") is False

    """

    __slots__ = ("__flags", "__rollback")

    def __init__(self, feature_flags: dict[str, bool]):
        self.__flags = feature_flags
        self.__rollback = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the state by running the rollback actions in reverse
        for action, args in reversed(self.__rollback):
            action(*args)

    def __setitem__(self, flag: str, value: bool):
        """Replace a flag state."""

        assert isinstance(flag, str), "Expected a `str` key."  # noqa: S101 - Assertions used in testing

        if flag in self.__flags:
            # Prepare an action that puts the current value back
            action = self.__flags.__setitem__, (flag, self.__flags[flag])
        else:
            # Prepare an action to remove the flag again
            action = self.__flags.__delitem__, (flag,)
        self.__rollback.append(action)

        self.__flags[flag] = value


class FeatureFlags:
    """
    Feature flags object that caches resolved flags.

    Flags are resolved in the following order:

    - CLI
    - Environment Variables
    - Settings

    """

    def __init__(self):
        self._cache: dict[str, bool] = {}

    @staticmethod
    def _resolve_from_environment(flag: str) -> bool | None:
        """
        Attempt to resolve from environment.
        """
        key = f"{settings.FEATURE_FLAG_PREFIX}{flag.translate(ENV_TRANSLATE)}"
        LOGGER.debug("Resolving flag %r from environment variable %s", flag, key)
        value = getenv(key, None)
        if value:
            return text_to_bool(value)
        return None

    @staticmethod
    def _resolve_from_settings(flag: str) -> bool | None:
        LOGGER.debug("Resolving flag %r from settings", flag)
        return settings.FEATURE_FLAGS.get(flag, None)

    def _resolve(self, flag: str, default: bool) -> bool:
        value = self._resolve_from_environment(flag)
        if value is not None:
            LOGGER.info("Flag %r resolved from environment: %s", flag, value)
            return value

        value = self._resolve_from_settings(flag)
        if value is not None:
            LOGGER.info("Flag %r resolved from settings: %s", flag, value)
            return value

        return default

    def _get(self, flag: str, default: bool) -> bool:
        try:
            return self._cache[flag]
        except KeyError:
            value = self._cache[flag] = self._resolve(flag, default)
            return value

    def set(self, flag: str, value: bool):
        """
        Set the state of the flag
        """
        self._cache[flag] = value

    def get(self, flag: str, *, default: bool = False):
        """
        Get the state of a flag

        :param flag: Name of flag
        :param default: Default flag state

        """
        return self._get(flag, default)

    def a_or_b(
        self,
        flag: str,
        option_a: Any | Callable[[], Any],
        option_b: Any | Callable[[], Any],
        *,
        default: bool = False,
    ):
        """
        Use one of two values (or results of callables),

        :param flag: Name of flag
        :param option_a: A value or callable that provides a value; used if flag is True
        :param option_b: B value or callable that provides a value; used if flag is False
        :param default: Default flag state

        """
        if self._get(flag, default):
            return option_a() if callable(option_a) else option_a
        return option_b() if callable(option_b) else option_b

    def if_enabled(
        self, flag: str, *, default: bool = False, disabled_return: Any = None
    ) -> Callable[[_F], _F]:
        """
        Decorator that is enabled by flag.

        :param flag: Name of flag
        :param default: Default flag state
        :param disabled_return: Return value if flag is disabled

        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self._get(flag, default):
                    return func(*args, **kwargs)
                return disabled_return

            return wrapper

        return decorator

    def modify(self) -> ModifyFeatureFlagsContext:
        """
        Apply changes to feature flags using a context manager that will roll back
        the changes on exit of a with block. Designed to simplify test cases.

        This should be used with a context manager:

            >>> feature_flags = FeatureFlags()
            >>> with feature_flags.modify() as patch:
            >>>     # Change a flag
            >>>     patch["foo"] = False
            >>>     # Clear a flag
            >>>     del patch["bar"]

        """
        return ModifyFeatureFlagsContext(self._cache)


DEFAULT = FeatureFlags()
get = DEFAULT.get  # pylint: disable=invalid-name
if_enabled = DEFAULT.if_enabled  # pylint: disable=invalid-name
a_or_b = DEFAULT.a_or_b
