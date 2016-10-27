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

