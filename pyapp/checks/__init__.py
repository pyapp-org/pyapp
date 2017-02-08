"""
Checks
~~~~~~

*Provides an interface and reports of simple pre-flight sanity checks for*
*your application.*

"""
from __future__ import absolute_import, unicode_literals

from .messages import *
from .registry import register, run_checks, Tags
from .built_in import security  # NOQA isort:skip
