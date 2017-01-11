"""
######################################
Configuration based Instance factories
######################################

Inversion of control style instance factories that return an object instance
based on a named definition from configuration. Makes use of
:py:mod:`pyapp.conf` to store instance definitions in settings.

An instance definition includes both the object type as well as arguments
provided at instantiation, this can be used to provide for example connections
to different multiple different database instances (that use the same database
engine and connection library).

The default instance factory also integrates with the :py:mod:`pyapp.checks`
framework to allow checks to be executed on the instances.

Usage::

    >>> foo_factory = NamedFactory('FOO')
    >>> instance = foo_factory()

or taking advantage of the factory being callable we can create a singleton
factory::

    >>> get_bar_instance = NamedSingletonFactory('BAR')
    >>> # Get iron bar instance
    >>> bar = get_bar_instance('iron')

"""
from __future__ import absolute_import

import importlib
import six
import threading

from pyapp import checks
from pyapp.conf import settings


class DefaultCache(dict):
    """
    Very similar to :py:class:`collections.defaultdict` (using __missing__)
    however passes the specified key to the default factory method.
    """

    def __init__(self, default_factory=None, **kwargs):
        super(DefaultCache, self).__init__(**kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        if not self.default_factory:
            raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value


def _import_type(type_name):
    """
    Import a type from a fully qualified module+type name

    :type type_name: str | unicode
    :rtype: type

    """
    module_name, type_name = type_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, type_name)


class NamedFactory(object):
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

    The NamedFactory is thread safe.

    """
    def __init__(self, setting, abc=None, default_name='default'):
        """
        Initialise a named factory.

        :param setting: Setting attribute that holds the definition of a 
            instance, this value should be an upper case.
        :param abc: The absolute base class that any new instance should be
            based on.
        :param default_name: The key within the settings to be returned as the
            default instance type if a value is not supplied.

        """
        self.setting = setting
        self.abc = abc
        self.default_name = default_name

        assert isinstance(setting, six.string_types) and setting.isupper()
        self._instance_definitions = getattr(settings, setting, {})
        self._type_definitions = DefaultCache(self._get_type_definition)
        self._type_definitions_lock = threading.RLock()

    def __call__(self, name=None):
        """
        Get a named instance.

        :param name: Named instance definition, default is to get the default
            instance type.
        :returns: New instanced of the named type.

        """
        return self.create_instance(name)

    @property
    def available(self):
        """
        Defined names available in settings.
        """
        return self._instance_definitions.keys()

    def _get_type_definition(self, name):
        try:
            type_name, kwargs = self._instance_definitions[name]
        except KeyError:
            raise KeyError("Setting definition `{}` not found".format(name))

        type_ = _import_type(type_name)
        if self.abc and not issubclass(type_, self.abc):
            raise TypeError("Setting definition `{}` is not a subclass of `{}`".format(
                type_name, self.abc
            ))

        return type_, kwargs

    def create_instance(self, name=None):
        """
        Get a named instance.

        :param name: Named instance definition; default value is defined by the
            ``default_name`` instance argument.
        :returns: New instance of the named type.

        """
        with self._type_definitions_lock:
            instance_type, kwargs = self._type_definitions[name or self.default_name]
        return instance_type(**kwargs)

    def checks(self, settings_, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.

        """
        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Instance definitions missing from settings.",
                hint="Add a {} entry into settings.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        instance_definitions = getattr(settings_, self.setting)
        if instance_definitions is None:
            return  # Nothing is defined so end now.

        if not isinstance(instance_definitions, dict):
            return checks.Critical(
                "Instance definitions defined in settings not a dict instance.",
                hint="Change setting {} to be a dict in settings file.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        # Take over the lock while checks are being performed
        with self._type_definitions_lock:
            # Backup definitions, replace and clear cache
            instance_definitions_orig = self._instance_definitions
            try:
                self._instance_definitions = instance_definitions
                self._type_definitions.clear()

                messages = []

                # Check default is defined
                if self.default_name not in self._instance_definitions:
                    messages.append(checks.Warn(
                        "Default definition not defined.",
                        hint="The default instance type `{}` is not defined.".format(self.default_name),
                        obj="settings.{}".format(self.setting)
                    ))

                # Check instance definitions
                for name in self._instance_definitions:
                    message = self.check_instance(name, **kwargs)
                    if isinstance(message, checks.CheckMessage):
                        messages.append(message)
                    elif message:
                        messages += message

                return messages

            finally:
                # Put definitions back and clear cache.
                self._instance_definitions = instance_definitions_orig
                self._type_definitions.clear()

    def check_instance(self, name, **_):
        """
        Checks for individual instances.

        :param name:
        :return:

        """
        definition = self._instance_definitions[name]
        if not isinstance(definition, (tuple, list)):
            return checks.Critical(
                "Instance definition is not a list/tuple.",
                hint="Change definition to be a list/tuple (type_name, kwargs) in settings.",
                obj='settings.{}[{}]'.format(self.setting, name)
            )

        if len(definition) != 2:
            return checks.Critical(
                "Instance definition is not a type name, kwarg (dict) pair.",
                hint="Change definition to be a list/tuple (type_name, kwargs) in settings.",
                obj='settings.{}[{}]'.format(self.setting, name)
            )

        type_name, kwargs = definition
        messages = []

        try:
            _import_type(type_name)
        except (ImportError, ValueError):
            messages.append(checks.Error(
                "Unable to import type `{}`.".format(type_name),
                hint="Check the type name in definition.",
                obj='settings.{}[{}]'.format(self.setting, name)
            ))

        if not isinstance(kwargs, dict):
            messages.append(checks.Critical(
                "Instance kwargs is not a dict.",
                hint="Change kwargs definition to be a dict.",
                obj='settings.{}[{}]'.format(self.setting, name)
            ))

        return messages


class NamedSingletonFactory(NamedFactory):
    """
    :py:class:`NamedFactory` that provides a single instance of an object.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalNamedSingletonFactory` is used.

    """
    def __init__(self, *args, **kwargs):
        super(NamedSingletonFactory, self).__init__(*args, **kwargs)

        super_create_instance = super(NamedSingletonFactory, self).create_instance
        self._instances = DefaultCache(super_create_instance)
        self._instances_lock = threading.RLock()

    def create_instance(self, name=None):
        """
        Get a named singleton instance.

        :param name: Named instance definition; default value is defined by the
            ``default_name`` instance argument.
        :returns: Instance of the named type.

        """
        with self._instances_lock:
            return self._instances[name]


class ThreadLocalNamedSingletonFactory(NamedFactory):
    """
    :py:class:`NamedFactory` that provides a single instance of an object per
    thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """
    def __init__(self, *args, **kwargs):
        super(ThreadLocalNamedSingletonFactory, self).__init__(*args, **kwargs)
        self._local = threading.local()

    @property
    def _local_cache(self):
        try:
            return getattr(self._local, 'cache')
        except AttributeError:
            super_create_instance = super(ThreadLocalNamedSingletonFactory, self).create_instance
            self._local.cache = cache = DefaultCache(super_create_instance)
            return cache

    def create_instance(self, name=None):
        """
        Get a named singleton instance.

        :param name: Named instance definition; default value is defined by the
            ``default_name`` instance argument.
        :returns: Instance of the named type.

        """
        return self._local_cache[name]
