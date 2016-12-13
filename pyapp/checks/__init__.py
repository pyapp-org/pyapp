"""
######
Checks
######

Provides a interface and reporting of simple pre-flight sanity checks for your application.

"""
from __future__ import absolute_import

from .messages import (
    CheckMessage,
    DEBUG, INFO, WARNING, ERROR, CRITICAL,
    Debug, Info, Warn, Error, Critical,
)
from .registry import register, run_checks, Tags

from .built_in import security  # NOQA isort:skip


__all__ = [
    'CheckMessage',
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
    'Debug', 'Info', 'Warn', 'Error', 'Critical',
    'register', 'run_checks', 'Tags'
]
