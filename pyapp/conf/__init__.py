"""
####################
Configuration loader
####################
"""
from __future__ import absolute_import
import logging
import os

from . import base_settings
from .loaders.module_loader import ModuleLoader

logger = logging.getLogger("pyapp.conf")

DEFAULT_ENV_KEY = 'PYAPP_SETTINGS'


class Settings(object):
    """
    Settings container
    """
    def __init__(self, base_settings=base_settings):
        # Copy values from base settings file.
        for key, value in ((k, getattr(base_settings, k)) for k in dir(base_settings) if k.isupper()):
            setattr(self, key, value)

        self.SETTINGS_SOURCES = []

    def __repr__(self):
        return '<{cls} {sources}>'.format(
            cls=self.__class__.__name__,
            sources=self.SETTINGS_SOURCES or 'Un-configured'
        )

    def load(self, loader):
        """
        Load settings from a loader instance.
        """
        loader_key = str(loader)
        if loader_key in self.SETTINGS_SOURCES:
            logger.warn("Settings already loaded: %s", loader_key)
            return  # Prevent circular loading

        logger.info("Loading settings from: %s", loader_key)

        # Apply values from loader
        for key, value in loader:
            setattr(self, key, value)

        # Store loader key to prevent circular loading
        self.SETTINGS_SOURCES.append(loader_key)

        # Handle instances of REQUIRE entries
        for source in self.INCLUDE_SETTINGS:
            pass

    def configure(self, default_settings, runtime_settings=None, env_settings_key=DEFAULT_ENV_KEY,
                  additional_loaders=None):
        """
        Configure the settings object

        :param default_settings: Your applications default settings file.
        :type default_settings: str | unicode
        :param runtime_settings: Settings defined for the current runtime (eg from the command line)
        :type runtime_settings: str | unicode
        :param env_settings_key: Environment variable key used to override the runtime_settings.
        :type env_settings_key: str | unicode

        """
        loaders = [ModuleLoader(default_settings)]

        # Add run time settings (which can be overridden or specified by an
        # enviornment variable).
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

