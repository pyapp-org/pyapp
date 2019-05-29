"""
######################################
PyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""
import logging

from .versioning import get_installed_version

# Configure a default null handler for logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Tim Savage <tim@savage.company>"
__version__ = get_installed_version("pyApp", __file__)
