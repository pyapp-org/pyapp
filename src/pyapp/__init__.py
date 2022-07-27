"""
######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""
import logging as _log

from pyapp.versioning import get_installed_version

# Configure a default null handler for logging.
_log.getLogger(__name__).addHandler(_log.NullHandler())

__author__ = "Tim Savage <tim@savage.company>"
