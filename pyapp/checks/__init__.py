"""
Checks
~~~~~~

*Provides an interface and reports of simple pre-flight sanity checks for*
*your application.*

Checks are executed via the CLI with the `checks` command. This will run all checks
and report the outcome. This is an invaluable tool for operations teams, checks can
be used to diagnose connectivity issues, for daily status checks or for PIV (Post
Implementation Verification) checking.

Checks are simply functions that accept a `settings` instance and optionally return
one or many message objects. Message objects come as Debug, Info, Warn, Error and
Critical varieties corresponding to the associated logging status definitions.

In addition to providing a basic description of why a check failed, messages can
also provide hints on how to correct an issue identified by a check.

An example check method::

    from pyapp.checks import register, Warning

    @register(Tags.security)
    def debug_enabled(settings, **_):
        '''
        Raise a warning if the debug setting is enabled.
        '''
        if settings.DEBUG:
            return Warning(
                msg="Debug mode is enabled",
                hint="Set DEBUG = False in your settings file"
            )

A good example of using checks is to ensure services defined in your settings file
are enabled and are accessible.

"""
from . import built_in  # NOQA
from .messages import *  # NOQA
from .registry import register
from .registry import Tags
