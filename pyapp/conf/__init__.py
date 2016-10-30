"""
#############
Configuration
#############

Provides a simple woy to add settings to your application.

"""
from __future__ import absolute_import
import logging
import os
import warnings

from . import default_settings
from .loaders import factory, ModuleLoader

logger = logging.getLogger("pyapp.conf")

DEFAULT_ENV_KEY = 'PYAPP_SETTINGS'


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

    def load(self, loader):
        """
        Load settings from a loader instance. A loader is an iterator that yields key/value pairs.

        See :py:class:`pyapp.conf.loaders.ModuleLoader` as an example.

        """
        loader_key = str(loader)
        if loader_key in self.SETTINGS_SOURCES:
            warnings.warn("Settings already loaded: {}".format(loader_key), category=ImportWarning)
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

settings = Settings()
