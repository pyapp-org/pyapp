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

ObjectLoader
------------

.. autoclass:: ObjectLoader

.. automodule:: pyapp.conf.loaders.file_loader

FileLoader
----------

.. autoclass:: FileLoader

.. automodule:: pyapp.conf.loaders.http_loader

HttpLoader
----------

.. autoclass:: HttpLoader

"""
import logging
import os
import warnings
from typing import List
from typing import Sequence

from pyapp.conf import base_settings
from pyapp.conf.loaders import factory
from pyapp.conf.loaders import Loader
from pyapp.conf.loaders import ModuleLoader

logger = logging.getLogger(__name__)

DEFAULT_ENV_KEY = "PYAPP_SETTINGS"


class ModifySettingsContext:
    """
    Context object used to make temporary modifications to settings.

    The main use-case for this feature is within test cases.

    Settings can be added/replaced/removed and when the context is exited the
    changes are reverted.

    ..note:

        Changes made to an item (eg dictionary) are not reverted at this time,
        to make changes to these items replace them with a clone.

    Example::

        >>> # Directly add settings (you shouldn't normally do this!)
        >>> settings.EXISTING_SETTING = "Foo"
        >>> settings.LIST_SETTING = ["Item A", "Item B"]
        >>> # Make some changes
        >>> with settings.modify() as modify:
        ...     # Add a new setting
        ...     modify.NEW_SETTING = 10
        ...     assert settings.NEW_SETTING == 10
        ...     # Remove an existing setting
        ...     del modify.EXISTING_SETTING
        ...     assert not hasattr(settings, "EXISTING_SETTING")
        ...     # Clone a list
        ...     modify.LIST_SETTING = modify.LIST_SETTING.clone()
        ...     modify.LIST_SETTING.append("New Item")
        >>> # Compare with initial state
        >>> assert not hasattr(settings, "NEW_SETTING")
        >>> assert settings.EXISTING_SETTING == "Foo"
        >>> assert settings.LIST_SETTING == ["Item A", "Item B"]

    """

    def __init__(self, settings_container: "Settings"):
        self.__dict__.update(_container=settings_container, _roll_back=[])

    def __enter__(self) -> "ModifySettingsContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the state by running the rollback actions in reverse
        for action, args in reversed(self._roll_back):
            action(*args)

    def __getattr__(self, item):
        # Proxy the underlying settings container
        return getattr(self._container, item)

    def __setattr__(self, key, value):
        items = self._container.__dict__

        if key in items:
            # Prepare an action that puts the current value back
            action = items.__setitem__, (key, items.get(key))
        else:
            # Prepare an action to remove the key again
            action = items.__delitem__, (key,)
        self._roll_back.append(action)

        items[key] = value

    def __delattr__(self, item):
        items = self._container.__dict__

        if item in items:
            # Prepare an action that puts the current value back
            action = items.__setitem__, (item, items.get(item))
            self._roll_back.append(action)

            del items[item]


class Settings:
    """
    Settings container
    """

    def __init__(self, base_settings_=None):
        base_settings_ = base_settings_ or base_settings

        # Copy values from base settings file.
        self.__dict__.update(
            (k, getattr(base_settings_, k)) for k in dir(base_settings_) if k.upper()
        )

        self.__dict__["SETTINGS_SOURCES"] = []  # pylint: disable=invalid-name

    def __getattr__(self, item):
        raise AttributeError("Setting not defined {!r}".format(item))

    def __setattr__(self, key, value):
        raise AttributeError("Readonly object")

    def __repr__(self) -> str:
        sources = self.SETTINGS_SOURCES or "UN-CONFIGURED"
        return f"{self.__class__.__name__}({sources})"

    @property
    def is_configured(self) -> bool:
        """
        Settings have been configured (or some initial settings have been loaded).
        """
        return bool(self.SETTINGS_SOURCES)

    def load(self, loader: Loader, apply_method=None):
        """
        Load settings from a loader instance. A loader is an iterator that yields key/value pairs.

        See :py:class:`pyapp.conf.loaders.ModuleLoader` as an example.

        """
        apply_method = apply_method or self.__dict__.__setitem__

        loader_key = str(loader)
        if loader_key in self.SETTINGS_SOURCES:
            warnings.warn(
                f"Settings already loaded: {loader_key}", category=ImportWarning
            )
            logger.warning("Settings already loaded: %s", loader_key)
            return  # Prevent circular loading

        logger.info("Loading settings from: %s", loader_key)

        # Apply values from loader
        with loader:
            for key, value in loader:
                logger.debug("Importing setting: %s", key)
                apply_method(key, value)

        # Store loader key to prevent circular loading
        self.SETTINGS_SOURCES.append(loader_key)

        # Handle instances of INCLUDE entries
        include_settings = self.__dict__.pop("INCLUDE_SETTINGS", None)
        if include_settings:
            for source_url in include_settings:
                self.load(factory(source_url), apply_method)

    def load_from_loaders(self, loader_list: Sequence[Loader], override: bool = True):
        """
        Load settings from a list of loaders.

        :param loader_list: List of loader instances.
        :param override: If True loaders override existing items else existing
            items are left untouched.

        """
        apply_method = None if override else self.__dict__.setdefault

        for loader in loader_list:
            self.load(loader, apply_method)

    def configure(
        self,
        default_settings: Sequence[str],
        runtime_settings: str = None,
        additional_loaders: Sequence[Loader] = None,
        env_settings_key: str = DEFAULT_ENV_KEY,
    ):
        """
        Configure the settings object

        :param default_settings: Your applications and extensions default settings.
        :param runtime_settings: Settings defined for the current runtime (eg from the command line)
        :param additional_loaders: Additional loaders to execute
        :param env_settings_key: Environment variable key used to override the runtime_settings.

        """
        logger.debug("Configuring settings...")

        loader_list: List[Loader] = [ModuleLoader(s) for s in default_settings]

        # Add run time settings (which can be overridden or specified by an
        # environment variable).
        runtime_settings = runtime_settings or os.environ.get(env_settings_key)
        if runtime_settings:
            loader_list.append(ModuleLoader(runtime_settings))

        # Append the additional loaders if defined
        if additional_loaders:
            loader_list.extend(additional_loaders)

        # Actually load settings from each loader
        self.load_from_loaders(loader_list)

        logger.debug("Settings loaded %s.", settings.SETTINGS_SOURCES)

    def modify(self) -> ModifySettingsContext:
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


settings = Settings()  # pylint: disable=invalid-name
