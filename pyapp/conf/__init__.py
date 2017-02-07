"""
Configuration
~~~~~~~~~~~~~

*Provides a simple woy to add settings to your application.*

Management of loading of settings from different file types and merging into
a simple easy to use settings object.

Usage::

    >>> from pyapp.conf import settings
    >>> # Configure default settings
    >>> settings.configure('my_app.default_settings')

    >>> settings.MY_CONFIG_VALUE
    'foo'

The settings object also has helper methods to simplify your testing::

    >>> from pyapp.conf import settings
    >>> with settings.modify() as patch:
    ...     patch.MY_CONFIG_VALUE = 'bar'
    ...     settings.MY_CONFIG_VALUE
    'bar'
    >>> settings.MY_CONFIG_VALUE
    'foo'

In addition to changing values new values can be added or existing values
removed using the `del` keyword. Once the context has been exited all changes
are reverted.

.. note::
    All settings must be UPPER_CASE. If a setting is not upper case it will not
    be imported into the settings object.

Settings
========

.. autoclass:: Settings
    :members: is_configured, load, configure, modify

Loaders
=======

.. automodule:: pyapp.conf.loaders

ModuleLoader
------------

.. autoclass:: ModuleLoader

.. automodule:: pyapp.conf.loaders.file_loader

FileLoader
----------

.. autoclass:: FileLoader

"""
from __future__ import absolute_import, unicode_literals

import logging
import os
import warnings

from . import default_settings
from .loaders import factory, ModuleLoader

logger = logging.getLogger(__name__)

DEFAULT_ENV_KEY = 'PYAPP_SETTINGS'


class ModifySettingsContext(object):
    """
    Context object used to make temporary modifications to settings.

    This is designed for usage with test cases.

    """
    def __init__(self, settings_container):
        self.__dict__.update(
            _container=settings_container,
            _roll_back=[]
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        container = self._container

        # Restore the state by running the rollback actions in reverse
        for action, args in reversed(self._roll_back):
            action(container, *args)

    def __getattr__(self, item):
        # Proxy the underlying settings container
        return getattr(self._container, item)

    def __setattr__(self, key, value):
        container = self._container

        if hasattr(container, key):
            # Prepare an action that puts the current value back
            action = setattr, (key, getattr(container, key))
        else:
            # Prepare an action to remove the key again
            action = delattr, (key,)
        self._roll_back.append(action)

        setattr(container, key, value)

    def __delattr__(self, item):
        container = self._container

        if hasattr(container, item):
            # Prepare an action that puts the current value back
            action = setattr, (item, getattr(container, item))
            self._roll_back.append(action)

            delattr(container, item)
        else:
            # Do nothing...
            pass


class Settings(object):
    """
    Settings container
    """
    def __init__(self, base_settings=default_settings):
        # Copy values from base settings file.
        self.__dict__.update((k, getattr(base_settings, k)) for k in dir(base_settings))

        self.SETTINGS_SOURCES = []

    def __repr__(self):
        return '{cls}({sources})'.format(
            cls=self.__class__.__name__,
            sources=self.SETTINGS_SOURCES or 'UN-CONFIGURED'
        )

    @property
    def is_configured(self):
        """
        Settings have been configured.
        """
        return bool(self.SETTINGS_SOURCES)

    def load(self, loader):
        """
        Load settings from a loader instance. A loader is an iterator that yields key/value pairs.

        See :py:class:`pyapp.conf.loaders.ModuleLoader` as an example.

        """
        loader_key = str(loader)
        if loader_key in self.SETTINGS_SOURCES:
            warnings.warn("Settings already loaded: {}".format(loader_key), category=ImportWarning)
            logger.warn("Settings already loaded: %s", loader_key)
            return  # Prevent circular loading

        logger.info("Loading settings from: %s", loader_key)

        # Apply values from loader
        self.__dict__.update(loader)

        # Store loader key to prevent circular loading
        self.SETTINGS_SOURCES.append(loader_key)

        # Handle instances of INCLUDE entries
        include_settings = self.__dict__.pop('INCLUDE_SETTINGS', None)
        if include_settings:
            for source_url in include_settings:
                self.load(factory(source_url))

    def configure(self, application_settings, runtime_settings=None, additional_loaders=None,
                  env_settings_key=DEFAULT_ENV_KEY):
        """
        Configure the settings object

        :param application_settings: Your applications default settings file.
        :type application_settings: str | unicode
        :param runtime_settings: Settings defined for the current runtime (eg from the command line)
        :type runtime_settings: str | unicode
        :param additional_loaders: Additional loaders to execute
        :type additional_loaders: list()
        :param env_settings_key: Environment variable key used to override the runtime_settings.
        :type env_settings_key: str | unicode

        """
        logger.debug("Configuring settings...")

        loaders = [ModuleLoader(application_settings)]

        # Add run time settings (which can be overridden or specified by an
        # environment variable).
        runtime_settings = runtime_settings or os.environ.get(env_settings_key)
        if runtime_settings:
            loaders.append(ModuleLoader(runtime_settings))

        # Append the additional loaders if defined
        if additional_loaders:
            loaders.extend(additional_loaders)

        # Actually load settings from each loader
        for loader in loaders:
            self.load(loader)

        logger.debug("Settings loaded %s.", settings.SETTINGS_SOURCES)

    def modify(self):
        """
        Apply changes to settings file using a context manager that will roll back the changes on exit of
        a with block. Designed to simplify test cases.

        This should be used with a context manager:

            >>> settings = Settings()
            >>> with settings.modify() as patch:
            >>>     # Change a setting
            >>>     patch.FOO = 'foo'
            >>>     # Remove a setting
            >>>     del patch.BAR


        :rtype: ModifySettingsContext

        """
        return ModifySettingsContext(self)

settings = Settings()
