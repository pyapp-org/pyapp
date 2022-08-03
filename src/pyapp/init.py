"""
Initialisation
~~~~~~~~~~~~~~

Initialisation of the framework

"""
import logging
import sys
from typing import Optional
from typing import Sequence
from typing import Union

import colorama
from pyapp import conf
from pyapp import extensions
from pyapp import feature_flags
from pyapp.conf import DEFAULT_ENV_KEY
from pyapp.injection import register_factory
from pyapp.logging import ColourFormatter
from pyapp.logging import InitHandler

log = logging.getLogger(__name__)


DEFAULT_LOG_HANDLER = logging.StreamHandler(sys.stderr)
"""
Log handler applied by default to root logger.
"""

DEFAULT_LOG_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
"""
Log formatter applied by default to root logger handler.
"""

DEFAULT_COLOR_LOG_FORMATTER = ColourFormatter(
    f"{colorama.Fore.YELLOW}%(asctime)s{colorama.Fore.RESET} "
    f"%(clevelname)s "
    f"{colorama.Fore.LIGHTBLUE_EX}%(name)s{colorama.Fore.RESET} "
    f"%(message)s"
)
"""
Log formatter applied by default to root logger handler.
"""

# Marker variable to ensure logging is not configured twice
_INIT_LOGGER: Optional[InitHandler] = None


def pre_configure_logging(
    *,
    log_handler: logging.Handler = DEFAULT_LOG_HANDLER,
    log_formatter: logging.Formatter = DEFAULT_LOG_FORMATTER,
):
    """
    Set some default logging so settings are logged.

    The main logging configuration is in settings leaving us with a chicken
    and egg situation.

    """
    global _INIT_LOGGER  # pylint: disable=global-statement

    # Configure formatter and setup init handler
    log_handler.formatter = log_formatter
    _INIT_LOGGER = InitHandler(log_handler)

    # Apply handler to root logger
    logging.root.setLevel(logging.DEBUG)
    logging.root.handlers = [_INIT_LOGGER]


def register_factories():
    """
    Register any abstract interface factories.
    """
    # pylint: disable=import-outside-toplevel
    from asyncio import AbstractEventLoop, get_event_loop

    register_factory(AbstractEventLoop, get_event_loop)


def load_extensions(
    extension_allow_list: Sequence[str] = None,
    *,
    command_group=None,
):
    """
    Load/Configure extensions.
    """
    entry_points = extensions.ExtensionEntryPoints(extension_allow_list)
    extensions.registry.load_from(entry_points.extensions())

    if command_group:
        extensions.registry.register_commands(command_group)


def configure_settings(
    default_settings: Union[str, Sequence[str]],
    runtime_settings: str = None,
    *,
    env_settings_key: str = DEFAULT_ENV_KEY,
):
    """
    Configure settings container.
    """
    application_settings = list(extensions.registry.default_settings)
    if default_settings:
        application_settings.append(default_settings)

    conf.settings.configure(
        application_settings, runtime_settings, env_settings_key=env_settings_key
    )


def configure_feature_flags(
    enable_feature_flags: Sequence[str] = None,
    disable_feature_flags: Sequence[str] = None,
):
    """
    Configure feature flags cache.
    """
    if enable_feature_flags:
        for flag in enable_feature_flags:
            feature_flags.DEFAULT.set(flag, True)

    if disable_feature_flags:
        for flag in disable_feature_flags:
            feature_flags.DEFAULT.set(flag, False)


def configure_logging(
    log_level=logging.INFO,
    *,
    log_handler: logging.Handler = DEFAULT_LOG_HANDLER,
    log_formatter: logging.Formatter = DEFAULT_LOG_FORMATTER,
):
    """
    Configure the logging framework.
    """
    global _INIT_LOGGER  # pylint: disable=global-statement

    # Prevent duplicate runs
    if _INIT_LOGGER:
        log_handler.formatter = log_formatter

        if conf.settings.LOGGING:
            log.info("Applying logging configuration.")

        # Replace root handler with the default handler
        logging.root.handlers.pop(0)
        logging.root.handlers.append(log_handler)

        if conf.settings.LOGGING:
            # Set a default version if not supplied by settings
            dict_config = conf.settings.LOGGING.copy()
            dict_config.setdefault("version", 1)
            logging.config.dictConfig(dict_config)

        # Configure root log level
        logging.root.setLevel(log_level)

        # Replay initial entries and remove
        _INIT_LOGGER.replay()
        _INIT_LOGGER = None


def startup_completed():
    """
    Startup has completed, perform required operations
    """
    extensions.registry.ready()


def shutdown_completed():
    """
    Shutdown has completed, perform required operations
    """
    logging.shutdown()


def initialise(
    default_settings: Union[str, Sequence[str]],
    log_level=logging.INFO,
    *,
    log_handler: logging.Handler = DEFAULT_LOG_HANDLER,
    log_formatter: logging.Formatter = DEFAULT_LOG_FORMATTER,
    extension_allow_list: Sequence[str] = None,
    runtime_settings: str = None,
    env_settings_key: str = DEFAULT_ENV_KEY,
    enable_feature_flags: Sequence[str] = None,
    disable_feature_flags: Sequence[str] = None,
):
    """
    Initialise a pyApp application outside a CLIApplication instance.

    Useful if you have a script or want to integrate pyApp into an existing application.
    """

    pre_configure_logging(log_handler=log_handler, log_formatter=log_formatter)
    register_factories()
    load_extensions(extension_allow_list=extension_allow_list)
    configure_settings(
        default_settings, runtime_settings, env_settings_key=env_settings_key
    )
    configure_feature_flags(enable_feature_flags, disable_feature_flags)
    configure_logging(log_level, log_handler=log_handler, log_formatter=log_formatter)
    startup_completed()
