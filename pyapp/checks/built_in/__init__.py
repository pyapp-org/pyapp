"""
Builtin Checks
~~~~~~~~~~~~~~

"""
from ..messages import Warn
from ..registry import register
from ..registry import Tags

try:
    from .settings_schema import settings_schema
except ImportError:
    settings_schema = None

W001 = Warn(
    "You should not have DEBUG set to True in deployment.",
    hint="Ensure DEBUG is set to False for deployment in settings.",
)


@register(Tags.security)
def debug_enabled(settings, **_):
    """
    Raise a warning if the debug setting is enabled.
    """
    if settings.DEBUG:
        return W001
    return None


# if settings_schema:
#     register(Tags.settings)(settings_schema)
