from __future__ import absolute_import, unicode_literals

import itertools
import threading
import six

from cached_property import cached_property

from pyapp import checks
from pyapp.conf import settings
from pyapp.conf.helpers.plugins import *
from .bases import DefaultCache, FactoryMixin, SingletonFactoryMixin, ThreadLocalSingletonFactoryMixin

__all__ = ('NamedConfiguration', 'DefaultCache',
           'NamedFactory', 'NamedSingletonFactory', 'ThreadLocalNamedSingletonFactory',
           'NamedPluginFactory', 'NamedSingletonPluginFactory', 'ThreadLocalNamedSingletonPluginFactory')


class NamedConfiguration(object):
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

    def __init__(self, setting, defaults=None, required_keys=None, optional_keys=None, default_name='default'):
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
        assert isinstance(setting, six.string_types) and setting.isupper()
        self.setting = setting
        self.default_name = default_name

        if defaults is not None:
            self.defaults = defaults
        if required_keys is not None:
            self.required_keys = required_keys
        if optional_keys is not None:
            self.optional_keys = optional_keys

        self._args = set(itertools.chain(self.required_keys, self.optional_keys, self.defaults))

    @cached_property
    def _config_definitions(self):
        return getattr(settings, self.setting, {})

    def _get_config_definition(self, name):
        try:
            kwargs = self._config_definitions[name]
        except KeyError:
            raise KeyError("Setting definition `{}` not found".format(name))

        config = self.defaults.copy()
        if self._args:
            config.update({k: kwargs[k] for k in self._args if k in kwargs})
        else:
            config.update(kwargs)
        return config

    def get(self, name=None):
        """
        Get named configuration from settings

        :param name: Name of value or default value.
        :return:

        """
        return self._get_config_definition(name or self.default_name)

    def checks(self, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.

        """
        settings_ = kwargs['settings']

        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Config definitions missing from settings.",
                hint="Add a {} entry into settings.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        config_definitions = getattr(settings_, self.setting)
        if config_definitions is None:
            return  # Nothing is defined so end now.

        if not isinstance(config_definitions, dict):
            return checks.Critical(
                "Config definitions defined in settings not a dict instance.",
                hint="Change setting {} to be a dict in settings file.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        messages = []

        # Check default is defined
        if self.default_name not in config_definitions:
            messages.append(checks.Warn(
                "Default definition not defined.",
                hint="Add a `{}` entry.".format(self.default_name,),
                obj="settings.{}".format(self.setting)
            ))

        # Check instance definitions
        for name in config_definitions:
            message = self.check_definition(config_definitions, name, **kwargs)
            if isinstance(message, checks.CheckMessage):
                messages.append(message)
            elif message:
                messages += message

        return messages
    checks.check_name = "{obj.setting}.check_configuration"

    def check_definition(self, config_definitions, name, **_):
        """
        Checks for individual definitions.

        :param config_definitions:
        :param name:
        :return:

        """
        definition = config_definitions[name]
        if not isinstance(definition, dict):
            return checks.Critical(
                "Config definition entry is not a dict.",
                hint="Change definition to be a dict in settings.",
                obj='settings.{}[{}]'.format(self.setting, name)
            )

        messages = []

        # Check required definitions exist
        for key in self.required_keys:
            if key not in definition:
                messages.append(checks.Critical(
                    "Config definition entry does not contain `{}` value.".format(key),
                    obj='settings.{}[{}]'.format(self.setting, name)
                ))

        # Check for un-known values
        if self._args:
            for key in definition:
                if key not in self._args:
                    messages.append(checks.Warn(
                        "Config definition entry contains unknown value `{}`.".format(key),
                        obj='settings.{}[{}][{}]'.format(self.setting, name, key)
                    ))

        return messages


class NamedFactory(FactoryMixin, NamedConfiguration):
    """
    Factory for creating instances from a named configuration.
    """
    def create_instance(self, name=None):
        raise NotImplementedError()


class NamedSingletonFactory(SingletonFactoryMixin, NamedFactory):
    """"
    :py:class:`NamedFactory` that provides a single instance of an object.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents.

    If your instance types are not thread safe it is recommended that the
    :py:class:`ThreadLocalNamedSingletonFactory` is used.
    """
    def create_instance(self, name=None):
        raise NotImplementedError()


class ThreadLocalNamedSingletonFactory(ThreadLocalSingletonFactoryMixin, NamedFactory):
    """
    :py:class:`NamedFactory` that provides a single instance of an object per
    thread.

    This instance factory type is useful for instance types that only require
    a single instance eg database connections, web service agents and that are
    not thread safe.

    """
    def create_instance(self, name=None):
        raise NotImplementedError()
