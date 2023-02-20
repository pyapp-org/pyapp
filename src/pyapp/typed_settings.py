"""Settings accessor definitions."""
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
