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
from typing import Type
from typing import TypeVar

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf.helpers.bases import DefaultCache
from pyapp.conf.helpers.bases import FactoryMixin
from pyapp.conf.helpers.bases import SingletonFactoryMixin
from pyapp.conf.helpers.bases import ThreadLocalSingletonFactoryMixin
from pyapp.exceptions import BadAlias
from pyapp.exceptions import CannotImport
from pyapp.exceptions import InvalidSubType
from pyapp.exceptions import NotFound
from pyapp.exceptions import NotProvided
from pyapp.utils import cached_property
from pyapp.utils import import_type

__all__ = (
    "NamedPluginFactory",
    "NamedSingletonPluginFactory",
    "ThreadLocalNamedSingletonPluginFactory",
    "NoDefault",
)


PT = TypeVar("PT", covariant=True)


NoDefault = "__NoDefault__"  # pylint: disable=invalid-name


# TODO: Remove when pylint handles typing.Dict correctly  pylint: disable=fixme
# pylint: disable=unsubscriptable-object
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
    def _instance_definitions(self):  # pylint: disable=method-hidden
        return getattr(settings, self.setting, {})

    @cached_property
    def has_default(self) -> bool:
        """
        This plugin does not have a default instance type
        """
        return self.default_name != NoDefault

    @property
    def available(self):
        """
        Defined names available in settings.
        """
        return self._instance_definitions.keys()

    def _resolve_instance_definition(self, name):
        alias_names = {name}
        while True:
            try:
                type_name, kwargs = self._instance_definitions[name]
            except KeyError:
                raise NotFound(f"Setting definition `{name}` not found") from None

            if type_name.upper() == "ALIAS":
                # Alias found
                name = kwargs.get("name")
                if not name:
                    raise BadAlias(f"Name not defined for alias `{name}`")

                # Circular alias protection
                if name in alias_names:
                    raise BadAlias(f"Circular aliases detected: {alias_names!r}")

                alias_names.add(name)

            else:
                return type_name, kwargs

    def _get_type_definition(self, name: str):
        type_name, kwargs = self._resolve_instance_definition(name)

        try:
            type_ = import_type(type_name)
        except (ImportError, AttributeError) as ex:
            raise CannotImport(
                f"Cannot import type `{type_name}` from config '{name}'."
            ) from ex

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
        if self.has_default:  # pylint: disable=using-constant-test
            name = name or self.default_name
        elif not name:
            raise NotProvided("A name is required if no default is specified.")

        with self._type_definitions_lock:
            instance_type, kwargs = self._type_definitions[name]
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
            return None  # Nothing is defined so end now.

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

        if type_name.upper() == "ALIAS":
            target_name = kwargs.get("name")
            if not target_name:
                messages.append(
                    checks.Critical(
                        "Name of alias target not defined",
                        hint="An alias entry must provide a `name` value that refers to another entry.",
                        obj=f"settings.{self.setting}[{name}]",
                    )
                )

            else:
                if target_name not in instance_definitions:
                    messages.append(
                        checks.Critical(
                            "Alias target not defined",
                            hint="The target specified by the alias does not exist, check the `name` value.",
                            obj=f"settings.{self.setting}[{name}][{target_name}]",
                        )
                    )

            if len(kwargs) > 1:
                messages.append(
                    checks.Warn(
                        "Alias contains unknown arguments",
                        hint="An alias entry must only provide a `name` value.",
                        obj=f"settings.{self.setting}[{name}]",
                    )
                )

        else:
            try:
                import_type(type_name)
            except (ImportError, ValueError, AttributeError):
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
