"""
######################################
PyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""
import logging

from .__version__ import __version__
from .versioning import get_installed_version

# Configure a default null handler for logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Tim Savage <tim@savage.company>"
version_info = tuple(int(p) for p in __version__.split("."))
