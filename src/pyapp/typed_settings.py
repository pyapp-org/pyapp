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
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Tuple


class SettingDescriptor:
    """Descriptor that can access a named setting."""

    __slots__ = ("setting",)

    def __init__(self, setting):
        self.setting = setting

    def __get__(self, instance, owner):
        from pyapp.conf import settings  # pylint: disable=import-outside-toplevel

        if settings.is_configured:
            return getattr(settings, self.setting)
        return None


class SettingsDefType(type):
    """Typed Settings definition type."""

    def __new__(cls, name: str, bases, dct: Dict[str, Any]):
        """Generate new type."""

        values = []
        descriptors = {}
        for key, value in dct.items():
            # Settings must be upper case (or constant style)
            if key.isupper():
                values.append((key, value))
                descriptors[key] = SettingDescriptor(key)

        # Update original dict.
        dct.update(descriptors)
        dct["_settings"] = tuple(values)
        dct["__slots__"] = ()

        return super().__new__(cls, name, bases, dct)


class SettingsDef(metaclass=SettingsDefType):
    """Typed settings definition."""


NamedConfig = Mapping[str, Mapping[str, Any]]
NamedPluginConfig = Mapping[str, Tuple[str, Mapping[str, Any]]]
