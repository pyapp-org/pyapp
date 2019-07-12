"""
*Configuration based Instance factories*

Inversion of control style plugin factories that return an object instance
based on a named definition from configuration. Makes use of
:py:mod:`pyapp.conf` to store instance definitions in settings.

An instance definition includes both the object type as well as arguments
provided at instantiation, this can be used to provide for example connections
to different multiple different database instances (that use the same database
engine and connection library).

The default instance factory also integrates with the :py:mod:`pyapp.checks`
framework to allow checks to be executed on the instances.

Usage::

    >>> foo_factory = NamedPluginFactory('FOO')
    >>> instance = foo_factory.create()

or taking advantage of the factory being callable we can create a singleton
factory::

    >>> get_bar_instance = NamedSingletonPluginFactory('BAR')
    >>> # Get iron bar instance
    >>> bar = get_bar_instance.create('iron')

"""
import threading

from abc import ABCMeta
from typing import TypeVar, Type

from pyapp import checks
from pyapp.conf import settings
from pyapp.exceptions import InvalidSubType, NotProvided, NotFound
from pyapp.utils import cached_property, import_type
from .bases import (
    DefaultCache,
    FactoryMixin,
    SingletonFactoryMixin,
    ThreadLocalSingletonFactoryMixin,
)

__all__ = (
    "NamedPluginFactory",
    "NamedSingletonPluginFactory",
    "ThreadLocalNamedSingletonPluginFactory",
    "NoDefault",
)


PT = TypeVar("PT", covariant=True)


class NoDefault(str):
    pass


class NamedPluginFactory(FactoryMixin[PT], metaclass=ABCMeta):
    """
    Factory object that generates a named instance from a definition in
    settings. Can optionally verify an instance type against a specified ABC
    (Abstract Base Class). The factory will cache imported types.

    Named instances are defined in settings using the following definition::

        MY_TYPE = {
            'default': (
                'my.module.MyClass', {
                    'param1': 123,
                    'param2': 'foo',
                }
            )
        }

    The :py:class:`NamedPluginFactory` is thread safe.

    """

    def __init__(
        self, setting: str, *, abc: Type[PT] = None, default_name: str = "default"
    ):
        """
        Initialise a named factory.

        :param setting: Setting attribute that holds the definition of a 
            instance, this value should be an upper case.
        :param abc: The absolute base class that any new instance should be
            based on.
        :param default_name: The key within the settings to be returned as the
            default instance type if a value is not supplied.

        """
        if not (isinstance(setting, str) and setting.isupper()):
            raise ValueError(f"Setting `{setting}` must be upper-case")
        self.setting = setting
        self.abc = abc
        self.default_name = default_name

        self._type_definitions = DefaultCache(self._get_type_definition)
        self._type_definitions_lock = threading.RLock()

        self._register_checks()

    @cached_property
    def _instance_definitions(self):
        return getattr(settings, self.setting, {})

    @cached_property
    def has_default(self) -> bool:
        return self.default_name is not NoDefault

    @property
    def available(self):
        """
        Defined names available in settings.
        """
        return self._instance_definitions.keys()

    def _get_type_definition(self, name: str):
        try:
            type_name, kwargs = self._instance_definitions[name]
        except KeyError:
            raise NotFound(f"Setting definition `{name}` not found") from None

        type_ = import_type(type_name)
        if self.abc and not issubclass(type_, self.abc):
            raise InvalidSubType(
                f"Setting definition `{type_name}` is not a subclass of `{self.abc}`"
            )

        return type_, kwargs

    def create(self, name: str = None) -> PT:
        """
        Get a named instance.

        :param name: Named instance definition; default value is defined by the
            ``default_name`` instance argument.
        :returns: New instance of the named type.

        """
        if self.has_default:
            name = name or self.default_name
        elif not name:
            raise NotProvided("A name is required if no default is specified.")

        with self._type_definitions_lock:
            instance_type, kwargs = self._type_definitions[name or self.default_name]
        return instance_type(**kwargs)

    def _register_checks(self):
        checks.register(self)

    def checks(self, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.
        """
        settings_ = kwargs["settings"]

        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Instance definitions missing from settings.",
                hint=f"Add a {self.setting} entry into settings.",
                obj=f"settings.{self.setting}",
            )

        instance_definitions = getattr(settings_, self.setting)
        if instance_definitions is None:
            return  # Nothing is defined so end now.

        if not isinstance(instance_definitions, dict):
            return checks.Critical(
                "Instance definitions defined in settings not a dict instance.",
                hint=f"Change setting {self.setting} to be a dict in settings file.",
                obj=f"settings.{self.setting}",
            )

        # Take over the lock while checks are being performed
        with self._type_definitions_lock:
            # Backup definitions, replace and clear cache, this is to make it
            # easier to write checks for instances.
            instance_definitions_orig = self._instance_definitions
            try:
                self._instance_definitions = instance_definitions
                self._type_definitions.clear()

                messages = []

                # Check default is defined
                if self.has_default and self.default_name not in instance_definitions:
                    messages.append(
                        checks.Warn(
                            "Default definition not defined.",
                            hint=f"The default instance type `{self.default_name}` is not defined.",
                            obj=f"settings.{self.setting}",
                        )
                    )

                # Check instance definitions
                for name in instance_definitions:
                    message = self.check_instance(instance_definitions, name, **kwargs)
                    if isinstance(message, checks.CheckMessage):
                        messages.append(message)
                    elif message:
                        messages += message

                return messages

            finally:
                # Put definitions back and clear cache.
                self._instance_definitions = instance_definitions_orig
                self._type_definitions.clear()

    checks.check_name = "{obj.setting}.check_configuration"

    def check_instance(self, instance_definitions, name, **_):
        """
        Checks for individual instances.
        """
        definition = instance_definitions[name]
        if not isinstance(definition, (tuple, list)):
            return checks.Critical(
                "Instance definition is not a list/tuple.",
                hint="Change definition to be a list/tuple (type_name, kwargs) in settings.",
                obj=f"settings.{self.setting}[{name}]",
            )

        if len(definition) != 2:
            return checks.Critical(
                "Instance definition is not a type name, kwarg (dict) pair.",
                hint="Change definition to be a list/tuple (type_name, kwargs) in settings.",
                obj=f"settings.{self.setting}[{name}]",
            )

        type_name, kwargs = definition
        messages = []

        try:
            import_type(type_name)
        except (ImportError, ValueError):
            messages.append(
                checks.Error(
                    f"Unable to import type `{type_name}`.",
                    hint="Check the type name in definition.",
                    obj=f"settings.{self.setting}[{name}]",
                )
            )

        if not isinstance(kwargs, dict):
            messages.append(
                checks.Critical(
                    "Instance kwargs is not a dict.",
                    hint="Change kwargs definition to be a dict.",
                    obj=f"settings.{self.setting}[{name}]",
                )
            )

        return messages


class NamedSingletonPluginFactory(SingletonFactoryMixin, NamedPluginFactory[PT]):
    """
    :py:class:`NamedPluginFactory` that provides a single instance of an object.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalNamedSingletonPluginFactory` is used.

    """


class ThreadLocalNamedSingletonPluginFactory(
    ThreadLocalSingletonFactoryMixin, NamedPluginFactory[PT]
):
    """
    :py:class:`NamedPluginFactory` that provides a single instance of a plugin per
    thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """
