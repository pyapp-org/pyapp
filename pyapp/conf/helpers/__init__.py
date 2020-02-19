"""
Configuration Helpers
~~~~~~~~~~~~~~~~~~~~~

The configuration helpers are a collection of tools that simplify building
configuration structures. They also provide a set of factory objects for the
generation of named instances from configuration.

The root helper is the NamedConfiguration, this object provides a simple
interface over configuration eg::

    >>> my_values = NamedConfiguration('MY_VALUES')
    >>> my_values.get('foo')
    '123'

    # With the following in your settings file
    MY_VALUES = {
        'foo': '123',
        'bar': '456',
    }


Simple factories
----------------

These factory objects come in three flavours:

- Basic - returns an instance for each request for a named object
- Singleton - returns the same instance (lazily created) for each named object
- ThreadLocalSingleton - returns an instance of each named object per thread

These classes are all ABS classes that the developer must inherit from and
provide an implementation of the ``create_instance`` method.

.. autoclass:: NamedFactory

.. autoclass:: NamedSingletonFactory

.. autoclass:: ThreadLocalNamedSingletonFactory


Plugin factories
----------------

Similar to simple factories, plugin factories also come in the same three
flavours, however they include the additional functionality of supporting the
creation of object instances based off configuration. The definition is
slightly more complex in your settings file.

.. autoclass:: NamedPluginFactory

.. autoclass:: NamedSingletonPluginFactory

.. autoclass:: ThreadLocalNamedSingletonPluginFactory


Provider factories
------------------

Extending from plugin factories providers provide an additional level of dynamic
configuration where configuration is obtained from data storage eg a database.

.. autoclass:: ProviderFactoryBase

"""
import itertools
from abc import ABCMeta
from typing import Any
from typing import Dict
from typing import Sequence

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf.helpers.bases import DefaultCache
from pyapp.conf.helpers.bases import FactoryMixin
from pyapp.conf.helpers.bases import FT
from pyapp.conf.helpers.bases import SingletonFactoryMixin
from pyapp.conf.helpers.bases import ThreadLocalSingletonFactoryMixin
from pyapp.conf.helpers.plugins import *
from pyapp.conf.helpers.providers import *
from pyapp.utils import cached_property

__all__ = (
    "NamedConfiguration",
    "DefaultCache",
    "NamedFactory",
    "NamedSingletonFactory",
    "ThreadLocalNamedSingletonFactory",
    "NamedPluginFactory",
    "NamedSingletonPluginFactory",
    "ThreadLocalNamedSingletonPluginFactory",
    "ProviderSummary",
    "ProviderFactoryBase",
)


class NamedConfiguration:
    """
    Factory object that obtains a `dict` of values from settings.

    Named configuration sets are defined in settings using the following structure::

        MY_TYPE = {
            'default': {
                'param1': 123,
                'param2': 'foo',
            }
        }

    """

    defaults = {}
    required_keys = []
    optional_keys = []
    default_name = "default"

    def __init__(
        self,
        setting: str,
        *,
        defaults: Dict[str, Any] = None,
        required_keys: Sequence[str] = None,
        optional_keys: Sequence[str] = None,
        default_name: str = None,
    ):
        """
        Initialise a named configuration.

        The defaults, required_keys and optional_keys are used to determine
        which values are required to be supplied and which values are valid for
        a particular entry. If none of these values are supplied then no keys
        are required, however if any are supplied then the restrictions are
        applied.

        Key checks are performed in checks, not during normal operation.

        :param setting: Setting attribute that holds the definition of a
            instance, this value should be an upper case.
        :param defaults: Default values.
        :param required_keys: Keys that must be included in config entry.
        :param optional_keys: Keys that may be included in config entry.
        :param default_name: The key within the settings to be returned as the
            default instance type if a value is not supplied.

        """
        if not (isinstance(setting, str) and setting.isupper()):
            raise ValueError(f"Setting `{setting}` must be upper-case")
        self.setting = setting

        if defaults is not None:
            self.defaults = defaults
        if required_keys is not None:
            self.required_keys = required_keys
        if optional_keys is not None:
            self.optional_keys = optional_keys
        if default_name is not None:
            self.default_name = default_name

        self._args = set(
            itertools.chain(self.required_keys, self.optional_keys, self.defaults)
        )

    @cached_property
    def _config_definitions(self) -> Dict[str, Any]:
        return getattr(settings, self.setting, {})

    def _get_config_definition(self, name: str) -> Dict[str, Any]:
        try:
            kwargs = self._config_definitions[  # pylint: disable=unsubscriptable-object
                name
            ]
        except KeyError:
            raise KeyError(f"Setting definition `{name}` not found")

        config = self.defaults.copy()
        if self._args:
            config.update({k: kwargs[k] for k in self._args if k in kwargs})
        else:
            config.update(kwargs)
        return config

    def get(self, name: str = None) -> Dict[str, Any]:
        """
        Get named configuration from settings

        :param name: Name of value or default value.

        """
        return self._get_config_definition(name or self.default_name)

    def checks(self, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.

        """
        settings_ = kwargs["settings"]

        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Config definitions missing from settings.",
                hint=f"Add a {self.setting} entry into settings.",
                obj=f"settings.{self.setting}",
            )

        config_definitions = getattr(settings_, self.setting)
        if config_definitions is None:
            return None  # Nothing is defined so end now.

        if not isinstance(config_definitions, dict):
            return checks.Critical(
                "Config definitions defined in settings not a dict instance.",
                hint=f"Change setting {self.setting} to be a dict in settings file.",
                obj=f"settings.{self.setting}",
            )

        messages = []

        # Check default is defined
        if self.default_name not in config_definitions:
            messages.append(
                checks.Warn(
                    "Default definition not defined.",
                    hint=f"Add a `{self.default_name}` entry.",
                    obj=f"settings.{self.setting}",
                )
            )

        # Check instance definitions
        for name in config_definitions:
            message = self.check_definition(config_definitions, name, **kwargs)
            if isinstance(message, checks.CheckMessage):
                messages.append(message)
            elif message:
                messages += message

        return messages

    checks.check_name = "{obj.setting}.check_configuration"

    def check_definition(
        self, config_definitions: Dict[str, Dict[str, Any]], name: str, **_
    ):
        """
        Checks for individual definitions.
        """
        definition = config_definitions[name]
        if not isinstance(definition, dict):
            return checks.Critical(
                "Config definition entry is not a dict.",
                hint="Change definition to be a dict in settings.",
                obj=f"settings.{self.setting}[{name}]",
            )

        messages = []

        # Check required definitions exist
        for key in self.required_keys:
            if key not in definition:
                messages.append(
                    checks.Critical(
                        f"Config definition entry does not contain `{key}` value.",
                        obj=f"settings.{self.setting}[{name}]",
                    )
                )

        # Check for un-known values
        if self._args:
            for key in definition:
                if key not in self._args:
                    messages.append(
                        checks.Warn(
                            f"Config definition entry contains unknown value `{key}`.",
                            obj=f"settings.{self.setting}[{name}][{key}]",
                        )
                    )

        return messages


# TODO: Remove when pylint handles typing.Dict correctly  pylint: disable=fixme
# pylint: disable=unsubscriptable-object
class NamedFactory(NamedConfiguration, FactoryMixin[FT], metaclass=ABCMeta):
    """
    Factory for creating instances from a named configuration.
    """


class NamedSingletonFactory(
    NamedConfiguration, SingletonFactoryMixin[FT], metaclass=ABCMeta
):
    """"
    :py:class:`NamedFactory` that provides a single instance of an object.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalNamedSingletonFactory` is used.
    """


class ThreadLocalNamedSingletonFactory(
    NamedConfiguration, ThreadLocalSingletonFactoryMixin[FT], metaclass=ABCMeta
):
    """
    :py:class:`NamedFactory` that provides a single instance of an object per
    thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """
