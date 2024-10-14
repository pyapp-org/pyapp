"""Base settings used to initialise settings object."""

from ..typed_settings import SettingsDef

DEBUG: bool = False
"""Enable debug mode"""


class LoggingSettings(SettingsDef):
    """Settings for logging."""

    LOG_LOGGERS: dict[str, dict] = {}
    """
    Simple method for configuring loggers that is merged into the default
    logging configuration. This allows for custom loggers to be configured
    without needing to duplicate the entire logging configuration.
    
    Example::
    
        LOG_LOGGERS = {
            "my_package.my_module": {
                "level": "INFO",
                "handlers": ["console"]
            }
        }
    
    """

    LOG_HANDLERS: dict[str, dict] = {}
    """
    Simple method for configuring log handlers that is merged into the default
    logging configuration. This allows for custom handlers to be configured
    without needing to duplicate the entire logging configuration.
    
    By default all handlers defined in this dict are added to the `root`
    handler, if this is not desired set the ``non_root`` argument to ``True``.
    
    See the `Logging Handlers <https://docs.python.org/3/library/logging.handlers.html>`_
    in the Python documentation for a complete list of builtin handlers.
    
    Example::
    
        LOG_HANDLERS = {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "stream": "/path/to/my/file.log",
                "maxBytes": 5_242_880,  # 5MiB
            },
            "special_file": {
                "class": "logging.FileHandler",
                "non_root": True,  # Don't assign to root logger
                "stream": "/path/to/my/special.log",
            }
        }
    
    """

    LOGGING: dict[str, dict] = {}
    """Logging configuration.
    
    The following configuration is applied by default::
    
        LOGGING = {
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stderr",
                },
            },
            "root": {
                # "level" : "INFO",  # Set from command line arg parser.
                "handlers": ["console"],
            }
        }
    
    """


###############################################################################
# Checks
class ChecksSettings(SettingsDef):
    """Checks settings."""

    CHECK_LOCATIONS: list[str] = []
    """Locations to import to ensure checks are registered."""


class FeatureFlagsSettings(SettingsDef):
    """Feature flag settings."""

    FEATURE_FLAGS: dict[str, bool] = {}
    """Feature flags definition, this is a simple configuration of::
    
        FEATURE_FLAGS = {
            "flag-name": True,  # State of True, False
        }
    
    """

    FEATURE_FLAG_PREFIX: str = "PYAPP_FLAG_"
    """Prefix applied to flag names for environment variables"""
