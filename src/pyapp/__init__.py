"""
######################################
pyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""

import logging

from pyapp.versioning import get_installed_version  # noqa

# Configure a default null handler for logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Tim Savage <tim@savage.company>"
