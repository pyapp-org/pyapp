from __future__ import unicode_literals

from pyapp.checks import Warn, register, Tags


W001 = Warn(
    "You should not have DEBUG set to True in deployment.",
    hint='Ensure DEBUG is set to False for deployment in settings.',
)


@register(Tags.security)
def debug_enabled(settings, **_):
    """
    Raise a warning if the debug setting is enabled.
    """
    if settings.DEBUG:
        return W001
