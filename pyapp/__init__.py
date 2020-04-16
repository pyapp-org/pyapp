"""
######################################
PyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""
import logging

from pyapp.__version__ import __version__
from pyapp.versioning import get_installed_version

# Configure a default null handler for logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Tim Savage <tim@savage.company>"
version_info = tuple(  # pylint: disable=invalid-name
    int(p) for p in __version__.split(".")
)
