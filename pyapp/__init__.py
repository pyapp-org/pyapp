# -*- coding: utf-8 -*-
"""
######################################
PyApp - A python application framework
######################################

*Let us handle the boring stuff!*

"""
from __future__ import unicode_literals

import logging
import os

from pkg_resources import get_distribution, DistributionNotFound
from .__version__ import __version__

# Configure a default null handler for logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = 'Tim Savage <tim@savage.company>'
