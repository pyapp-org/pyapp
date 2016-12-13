"""
######################################
Configuration based Instance factories
######################################

Instance factories that generate an instance of an object based on 
configuration. Makes use of :py:mod:`pyapp.conf` for the definition of named
instance definition.

The default instance factory also integrates with the :py:mod:`pyapp.checks`
framework to allow checks to be executed on the instances.

Usage::

    >>> foo_factory = NamedABCFactory('FOO')
    >>> instance = foo_factory.get_instance()

or taking advantage of the factory being callable we can create a singleton
factory::

    >>> get_bar_instance = NamedSingletonABCFactory('BAR')
    >>> # Get iron bar instance
    >>> bar = get_bar_instance('iron')

"""
from __future__ import absolute_import

import importlib
import six
import threading

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
        self.abc = abc
        self.default_name = default_name

        assert isinstance(setting, six.string_types) and setting.isupper()
        try:
            self._instance_definitions = getattr(settings, setting)
        except AttributeError:
            raise ValueError("Instance definitions for `{}` not found in settings.".format(setting))

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


class NamedSingletonFactory(NamedFactory):
    """
    :py:class:`NamedFactory` that provides a single instance of an object.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadSafeNamedSingletonFactory` is used.

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


# class ThreadSafeNamedSingletonFactory(NamedFactory):
#     """
#     :py:class:`NamedABCFactory` that provides a single instance of an object
#     for each thread.
#
#     This instance factory type is useful for instance types that are not
#     thread safe.
#
#     """
#     def __init__(self, *args, **kwargs):
#         super(ThreadSafeNamedSingletonFactory, self).__init__(*args, **kwargs)
#
#         import threading
#         self._local = threading.local()
#