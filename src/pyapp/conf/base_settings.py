"""
Default Settings
~~~~~~~~~~~~~~~~

.. auto
"""
from typing import Any
from typing import Dict
from typing import Sequence

DEBUG: bool = False
"""
Enable debug mode
"""


###############################################################################
# Logging

LOGGING: Dict[str, Any] = {}
"""
Logging configuration.

The following configuration is applied by default::

    LOGGING = {
        'formatters': {
            'default': {
                'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stderr',
            },
        },
        'root': {
            # 'level' : 'INFO',  # Set from command line arg parser.
            'handlers': ['console'],
        }
    }

"""


###############################################################################
# Checks

CHECK_LOCATIONS: Sequence[str] = []
"""
Locations to import to ensure checks are registered.
"""
