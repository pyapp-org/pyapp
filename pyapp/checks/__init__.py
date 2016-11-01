"""
######
Checks
######

Provides a interface and reporting of simple pre-flight sanity checks for your application.

"""
from __future__ import absolute_import

from .messages import (
    DEBUG, INFO, WARNING, ERROR, CRITICAL,
    Debug, Info, Warn, Error, Critical,
    CheckMessage
)

from .registry import register, run_checks, Tags
