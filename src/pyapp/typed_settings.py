"""
Typed Settings
~~~~~~~~~~~~~~

Building on the standard settings features that is a core part of pyApp typed
settings provides a more convenient way to define and access settings.

Default settings are defined using a `SettingsDef` object along with the expected
type via type annotations. The settings can then be accessed at runtime using the
same definition.

For example settings are defined in the `default_settings.py` file as:

.. code-block:: python

    from pyapp.typed_settings import SettingsDef

    class MyAppSettings(SettingsDef):
        MY_CONFIG_VALUE: str = "Foo"

`MY_CONFIG_VALUE` is added to `pyapp.conf.settings` just like any other setting
and can be overridden by any other settings file.

Where typed settings really shine is using the settings in your application.
The `SettingsDef` object can be imported from the `default_settings` file and
used to access the runtime settings values using the same definition with all
the benefits of auto-completion and typing.

.. code-block:: python

    from myapp.default_settings import MyAppSettings

    print(MyAppSettings.MY_CONFIG_VALUE)

"""

from collections.abc import Mapping
from typing import Any


class SettingDescriptor:
    """Descriptor that can access a named setting."""

    __slots__ = ("setting",)

    def __init__(self, setting):
        self.setting = setting

    def __get__(self, instance, owner):
        from pyapp.conf import settings

        return getattr(settings, self.setting, None)


class SettingsDefType(type):
    """Typed Settings definition type."""

    def __new__(cls, name: str, bases, dct: dict[str, Any], *, prefix: str = ""):
        """Generate new type."""

        if prefix and not prefix.isupper():
            raise ValueError("Prefix must be upper snake case.")

        values = []
        descriptors = {}
        for key, value in dct.items():
            # Settings must be upper case (or constant style)
            if key.isupper():
                values.append((key, value))
                descriptors[key] = SettingDescriptor(f"{prefix}{key}")

        # Update original dict.
        dct.update(descriptors)
        dct["_settings"] = tuple(values)
        dct["__slots__"] = ()

        return super().__new__(cls, name, bases, dct)


class SettingsDef(metaclass=SettingsDefType):
    """Typed settings definition."""


NamedConfig = Mapping[str, Mapping[str, Any]]
NamedPluginConfig = Mapping[str, tuple[str, Mapping[str, Any]]]
