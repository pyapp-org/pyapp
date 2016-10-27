INCLUDE_SETTINGS = []
"""
Include settings for a location.

This could be from a JSON file on disk/via HTTP/from S3 etc or a different
Python settings file.
"""

DEBUG = False
"""
Enable debug mode
"""

###############################################################################
# Logging

LOGGING = {
    'formatters': {
        'default': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    }
}

