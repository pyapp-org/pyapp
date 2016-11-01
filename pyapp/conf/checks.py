from pyapp import checks


@checks.register(checks.Tags.configuration)
def debug_enabled(settings, **_):
    """
    Raise a warning if the debug setting is enabled.
    """
    if settings.DEBUG:
        return checks.Warn(
            "Debug is enabled.",
            hint='Ensure the DEBUG setting is set to False for production.',
            obj='settings'
        )
