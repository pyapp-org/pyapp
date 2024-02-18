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
from functools import wraps
from os import getenv
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from pyapp.conf import settings
from pyapp.utils import text_to_bool

LOGGER = logging.getLogger(__name__)
ENV_TRANSLATE = str.maketrans(
    " -abcdefghijklmnopqrstuvwxyz", "__ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
_F = TypeVar("_F", bound=Callable[..., Any])


class FeatureFlags:
    """
    Feature flags object that caches resolved flags.

    Flags are resolved in the following order:

    - CLI
    - Environment Variables
    - Settings

    """

    __slots__ = ("_cache",)

    def __init__(self):
        self._cache: Dict[str, bool] = {}

    @staticmethod
    def _resolve_from_environment(flag: str) -> Optional[bool]:
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
    def _resolve_from_settings(flag: str) -> Optional[bool]:
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
        option_a: Union[Any, Callable[[], Any]],
        option_b: Union[Any, Callable[[], Any]],
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


DEFAULT = FeatureFlags()
get = DEFAULT.get  # pylint: disable=invalid-name
if_enabled = DEFAULT.if_enabled  # pylint: disable=invalid-name
