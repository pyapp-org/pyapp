from typing import Sequence

from pyapp.conf import Settings
from pyapp.conf.schema import SettingsSchema, ValidationError, UnknownSetting
from ..messages import CheckMessage, Error, Warn


def settings_schema(settings: Settings, **_) -> Sequence[CheckMessage]:
    """
    Checking settings
    """
    messages = []

    # Build a schema from loaders
    schema = SettingsSchema()
    for loader in settings.default_loaders:
        for warn in schema.append_loader(loader):
            messages.append(
                Warn(
                    f"Duplicate value {warn}.",
                    hint="This value is defined multiple times check that extensions"
                         "are not conflicting.",
                )
            )

    # Validate settings
    for key, value in ((k, getattr(settings, k)) for k in dir(settings) if k.isupper()):
        # Ignore expected auto generated entries
        if key in ("LOGGING", "SETTINGS_SOURCES"):
            continue

        try:
            schema.validate_value(key, value)
        except UnknownSetting:
            messages.append(
                Warn(
                    f"Unknown value {key}.",
                    hint="This value is not defined in the setting schema and could be miss-spelled.",
                )
            )
        except ValidationError as ex:
            messages.append(Error(f"Invalid value {key}.", hint=str(ex)))

    return messages
