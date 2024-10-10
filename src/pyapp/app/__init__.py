"""
Application
~~~~~~~~~~~

*Application with bindings for commands*

The application object handles all the initial configuration to set up the
run-time environment.

Quick demo::

    >>> from pyapp.app import CliApplication

    >>> app = CliApplication()

    >>> @app.command()
    >>> def hello(*, verbose: bool):
    ...     if verbose:
    ...         print("Being verbose!")
    ...     print("Hello")

    >>> if __name__ == '__main__':
    ...     app.dispatch()


This example provides an application with a command `hello` that takes an
optional `verbose` flag. The framework also provides help, configures and loads
settings (using :py:mod:`pyapp.conf`), an interface to the checks framework
and configures the Python logging framework.

There are however a few more things that are required to get this going. The
:py:class:`CliApplication` class expects a certain structure of your
application to allow for it's (customisable) defaults to be applied.

Your application can have one of two structures

An application::

    my_app/__init__.py          # Include a __version__ variable
           __main__.py          # This is where the quick demo is located
           default_settings.py  # The default settings file
           checks.py            # Optional checks file


A single script::

    my_app.py                   # A script that contains the `CliApplication`


Generation of CLI from command Signature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 4.4

As of pyApp 4.4 command functions can supply all required arguments in the function
signature.

As an example consider the command function:

.. code-block:: python

    @app.command
    def my_command(
        arg1: str,
        *,
        arg2: bool= Arg(help="Enable the argilizer"),
        arg3: int = 42,
        arg4: str = Arg("-a", choices=("foo", "bar"), default="foo")
    ):
        ...

This translates into the following on the CLI:

.. code-block:: shell

    > python -m my_app my_command --help
    usage: my_app my_command [-h] ARG1 [--arg2] [--arg3 ARG3]
                             [--arg4 {foo,bar}]

    positional arguments:
      ARG1

    optional arguments:
      -h, --help  show this help message and exit
      --arg2    Enable the argilizer
      --arg3
      --arg4 {foo,bar}


The following types are supported as arguments:

    - Basic types eg int, str, float, this covers any type that can be provided
      to argparse in the type field.

    - bool, this is made into an argparse `store_true` action.

    - Enum types using the pyApp EnumAction.

    - Generic types
        - Mapping/Dict as well as a basic dict for Key/Value pairs

        - Sequence/List for typed sequences, ``nargs="+"`` for positional arguments
          of ``action="append"`` for optional.

        - Tuple for typed sequences of a fixed size eg ``nargs=len(tuple)``. Only
          the first type is used, the others are ignored.

    - FileType from ``argparse``.

.. tip:: Too get access to the parse results from `argparse` provide a vairable
    with the type ``pyapp.app.CommandOptions``.


CliApplication
--------------

.. autoclass:: CliApplication
    :members: command, create_command_group, default, dispatch

Events
~~~~~~

CliApplication generates the following events, all methods are provided with the
``argparse`` namespace.

+--------------------------------------------------------------+----------------------------------------------------+
| ``pre_dispatch[[argparse.Namespace], None]``                 | Generated before command dispatch is called        |
+--------------------------------------------------------------+----------------------------------------------------+
| ``post_dispatch[[Optional[int], argparse.Namespace], None]`` | Generated after command dispatch returns without   |
|                                                              | error includes the return code if one is provided. |
+--------------------------------------------------------------+----------------------------------------------------+
| ``dispatch_error[[Exception, argparse.Namespace], None]``    | Generated when an exception is raised in a command |
|                                                              | function before the standard exception reporting.  |
+--------------------------------------------------------------+----------------------------------------------------+


Arguments
---------

.. automodule:: pyapp.app.arguments


Argument Types
--------------

.. automodule:: pyapp.app.argument_types


Argument Actions
----------------

.. automodule:: pyapp.app.argument_actions

"""

import argparse
import io
import logging.config
import os
import sys
import warnings
from argparse import ArgumentParser
from argparse import Namespace as CommandOptions
from collections.abc import Callable, Sequence

import argcomplete
import colorama

from .. import conf, extensions, feature_flags
from ..app import builtin_handlers
from ..conf.base_settings import LoggingSettings
from ..events import Event
from ..exceptions import ApplicationExit
from ..injection import register_factory
from ..utils.inspect import import_root_module
from . import init_logger
from .argument_actions import *  # noqa
from .arguments import *  # noqa
from .logging_formatter import ColourFormatter

logger = logging.getLogger(__name__)


def _key_help(key: str) -> str:
    """Formats a key value from environment vars."""
    if key in os.environ:
        return f"{key} [{os.environ[key]}]"
    return key


class CliApplication(CommandGroup):  # noqa: F405
    """Application interface that provides a CLI interface.

    :param root_module: The root module for this application (used for discovery of
        other modules)
    :param prog: Name of your application; defaults to `sys.argv[0]`
    :param description: A description of your application for `--help`.
    :param version: Specify a specific version; defaults to
        `getattr(root_module, '__version__')`
    :param ext_allow_list: Sequence of extension names or globs that are allowed;
        default is `None` or all extensions.
    :param ext_block_list: Sequence of extension names or globs that are blocked;
        default is `None` or no blocking.
    :param application_settings: The default settings for this application;
        defaults to `root_module.default_settings`
    :param application_checks: Location of application checks file; defaults to
        `root_module.checks` if it exists.
    :param env_settings_key: Key used to define settings file in environment.
    :param env_loglevel_key: Key used to define log level in environment

    """

    default_log_handler = logging.StreamHandler(sys.stderr)
    """Log handler applied by default to the root logger."""

    default_log_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    """Log formatter applied by default to the root logger handler."""

    default_color_log_formatter = ColourFormatter(
        f"{colorama.Fore.YELLOW}%(asctime)s{colorama.Fore.RESET} "
        f"%(clevelname)s "
        f"{colorama.Fore.LIGHTBLUE_EX}%(name)s{colorama.Fore.RESET} "
        f"%(message)s"
    )
    """Log formatter with colour applied by default to the root logger handler."""

    env_settings_key = conf.DEFAULT_ENV_KEY
    """Key used to define settings reference in environment."""

    env_loglevel_key = "PYAPP_LOGLEVEL"
    """Key used to define log level in environment."""

    additional_handlers = (
        builtin_handlers.checks,
        builtin_handlers.extensions,
        builtin_handlers.settings,
    )
    """Handlers to be added when builtin handlers are registered."""

    # Events
    pre_dispatch = Event[Callable[[argparse.Namespace], None]]()
    post_dispatch = Event[Callable[[int | None, argparse.Namespace], None]]()
    dispatch_error = Event[Callable[[Exception, argparse.Namespace], None]]()

    def __init__(  # noqa: PLR0913
        self,
        root_module=None,
        *,
        prog: str = None,
        description: str = None,
        epilog: str = None,
        version: str = None,
        ext_white_list: Sequence[str] = None,
        ext_allow_list: Sequence[str] = None,
        ext_block_list: Sequence[str] = None,
        application_settings: str = None,
        application_checks: str = None,
        env_settings_key: str = None,
        env_loglevel_key: str = None,
    ):
        root_module = root_module or import_root_module()
        self.root_module = root_module
        super().__init__(ArgumentParser(prog, description=description, epilog=epilog))
        self.application_version = version or getattr(
            root_module, "__version__", "Unknown"
        )
        self.ext_allow_list = ext_allow_list
        if ext_white_list:
            warnings.warn(
                "ext_white_list is deprecated, use ext_allow_list",
                DeprecationWarning,
                stacklevel=2,
            )
            self.ext_allow_list = ext_white_list
        self.ext_block_list = ext_block_list

        # Determine application settings (disable for standalone scripts)
        if application_settings is None and root_module.__name__ != "__main__":
            application_settings = f"{root_module.__name__}.default_settings"
        self.application_settings = application_settings

        # Determine application checks
        if application_checks is None:
            application_checks = f"{root_module.__name__}.checks"
        self.application_checks = application_checks

        # Override default value
        if env_settings_key is not None:
            self.env_settings_key = env_settings_key
        if env_loglevel_key is not None:
            self.env_loglevel_key = env_loglevel_key

        # Configure Logging as early as possible
        self._init_logger = init_logger.InitHandler(self.default_log_handler)
        self.pre_configure_logging()

        self._init_parser()
        self.register_builtin_handlers()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<module {self.root_module.__name__}>)"

    def __str__(self) -> str:
        return self.application_summary

    @property
    def application_name(self) -> str:
        """Name of the application."""
        return self.parser.prog

    @property
    def application_summary(self) -> str:
        """Summary of the application, name version and description."""
        description = self.parser.description
        if description:
            return f"{self.application_name} version {self.application_version} - {description}"
        return f"{self.application_name} version {self.application_version}"

    def _init_parser(self):
        # Create argument parser
        self.argument(
            "--settings",
            help="Settings to load; either a Python module or settings URL. "
            f"Defaults to the env variable: {_key_help(self.env_settings_key)}",
        )
        self.argument(
            "--version",
            action="version",
            version=f"%(prog)s version: {self.application_version}",
        )
        self.argument(
            "--nocolor",
            "--nocolour",
            dest="no_color",
            action="store_true",
            help="Disable colour output.",
        )

        # Log configuration
        arg_group = self.argument_group(
            title="logging arguments", description="Customise log output"
        )
        arg_group.add_argument(
            "--log-level",
            default=os.environ.get(self.env_loglevel_key, "DEFAULT"),
            choices=("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"),
            help="Specify the log level to be used. "
            f"Defaults to env variable: {_key_help(self.env_loglevel_key)}",
        )
        # arg_group.add_argument(
        #     "--log-file",
        #     type=FileType(mode="w", encoding="UTF-8"),
        #     help="Optionally override log file output.",
        # )
        arg_group.add_argument(
            "--log-color",
            "--log-colour",
            dest="log_color",
            default=None,
            action="store_true",
            help="Force coloured output from logger (on console).",
        )
        arg_group.add_argument(
            "--log-nocolor",
            "--log-nocolour",
            dest="log_color",
            action="store_false",
            help="Disable coloured output from logger (on console).",
        )

        # Global check values
        arg_group = self.argument_group(
            title="check arguments", description="Enable and configure run-time checks"
        )
        arg_group.add_argument(
            "--checks",
            dest="checks_on_startup",
            action="store_true",
            help="Run checks on startup, any serious error will result "
            "in the application terminating.",
        )
        arg_group.add_argument(
            "--checks-level",
            dest="checks_message_level",
            default="INFO",
            choices=("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"),
            help="Minimum level of check message to display",
        )

        # Feature flags
        arg_group = self.argument_group(
            title="feature flags", description="Enable/Disable feature flags"
        )
        arg_group.add_argument(
            "--enable-flag",
            dest="enable_feature_flags",
            action="append",
            help="Enable a named feature flag; this argument can be used multiple times",
        )
        arg_group.add_argument(
            "--disable-flag",
            dest="disable_feature_flags",
            action="append",
            help="Disable a named feature flag; this argument can be used multiple times",
        )

    def register_builtin_handlers(self):
        """Register any built in handlers."""
        # Register any additional handlers
        for additional_handler in self.additional_handlers:
            additional_handler(self)

    def pre_configure_logging(self):
        """Set some default logging so settings are logged.

        The main logging configuration is in settings leaving us with a chicken
        and egg situation.
        """
        self.default_log_handler.formatter = self.default_log_formatter

        # Apply handler to root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.handlers = [self._init_logger]

    @staticmethod
    def register_factories():
        """Register any abstract interface factories."""
        # pylint: disable=import-outside-toplevel
        from asyncio import AbstractEventLoop, get_event_loop

        register_factory(AbstractEventLoop, get_event_loop)

    def load_extensions(self):
        """Load/Configure extensions."""
        entry_points = extensions.ExtensionEntryPoints(
            self.ext_allow_list, self.ext_block_list
        )
        extensions.registry.load_from(entry_points.extensions())
        extensions.registry.register_commands(self)

    def configure_settings(self, opts: CommandOptions):
        """Configure settings container."""
        application_settings = list(extensions.registry.default_settings)
        if self.application_settings:
            application_settings.append(self.application_settings)

        conf.settings.configure(
            application_settings, opts.settings, env_settings_key=self.env_settings_key
        )

    @staticmethod
    def configure_feature_flags(opts: CommandOptions):
        """Configure feature flags cache."""
        if opts.enable_feature_flags:
            for flag in opts.enable_feature_flags:
                feature_flags.DEFAULT.set(flag, True)

        if opts.disable_feature_flags:
            for flag in opts.disable_feature_flags:
                feature_flags.DEFAULT.set(flag, False)

    def get_log_formatter(self, log_color) -> logging.Formatter:
        """Get log formatter."""
        log_handler = self.default_log_handler

        # Auto-detect colour mode
        if (
            log_color is None
            and isinstance(log_handler, logging.StreamHandler)
            and hasattr(log_handler.stream, "isatty")
        ):
            log_color = log_handler.stream.isatty()

        # Enable colour if specified.
        if log_color:
            return self.default_color_log_formatter

        return self.default_log_formatter

    @staticmethod
    def _apply_logging_settings():
        """Build dict-config from settings and apply to logging."""

        dict_config = LoggingSettings.LOGGING.copy() or {}

        # Merge in other settings
        if LoggingSettings.LOG_HANDLERS:
            dict_config.setdefault("handlers", {}).update(LoggingSettings.LOG_HANDLERS)
        if LoggingSettings.LOG_LOGGERS:
            dict_config.setdefault("loggers", {}).update(LoggingSettings.LOG_LOGGERS)

        # Only apply config if we have something to apply
        if dict_config:
            dict_config.setdefault("version", 1)
            logging.config.dictConfig(dict_config)

    def configure_logging(self, opts: CommandOptions):
        """Configure the logging framework."""
        # Prevent duplicate runs
        if hasattr(self, "_init_logger"):
            self.default_log_handler.formatter = self.get_log_formatter(opts.log_color)

            # Replace root handler with the default handler
            logging.root.handlers.pop(0)
            logging.root.handlers.append(self.default_log_handler)
            self._apply_logging_settings()

            # Configure root log level
            loglevel = opts.log_level
            if loglevel == "DEFAULT":
                handler = self.resolve_handler(opts)
                loglevel = getattr(handler, "loglevel", logging.INFO)
            logging.root.setLevel(loglevel)

            # Replay initial entries and remove
            self._init_logger.replay()
            del self._init_logger

    def checks_on_startup(self, opts: CommandOptions):
        """Run checks on startup."""
        # pylint: disable=import-outside-toplevel
        from pyapp.checks.report import execute_report

        if opts.checks_on_startup:
            out = io.StringIO()

            serious_error = execute_report(
                out,
                self.application_checks,
                opts.checks_message_level,
                verbose=True,
                header=f"Check report for {self.application_summary}",
            )
            if serious_error:
                logger.error("Check results:\n%s", out.getvalue())
                sys.exit(4)
            else:
                logger.info("Check results:\n%s", out.getvalue())

    def exception_report(self, exception: BaseException, opts: CommandOptions):
        """Generate a report for any unhandled exceptions caught by the framework."""
        logger.exception(
            "Un-handled exception %s caught executing handler: %s",
            exception,
            getattr(opts, self.handler_dest),
        )
        return False

    @staticmethod
    def logging_shutdown():
        """Call at shutdown to ensure logging is cleaned up."""
        logging.shutdown()

    def dispatch(self, args: Sequence[str] = None) -> None:
        """Dispatch command to registered handler."""
        logger.info("Starting %s", self.application_summary)

        # Initialisation phase
        _set_running_application(self)
        self.register_factories()
        self.load_extensions()

        # Parse arguments phase
        argcomplete.autocomplete(self.parser)
        opts = self.parser.parse_args(args)

        # Load settings and configure logger
        self.configure_settings(opts)
        self.configure_feature_flags(opts)
        self.configure_logging(opts)

        handler_name = getattr(opts, ":handler", None)
        if handler_name != "checks":
            self.checks_on_startup(opts)
        else:
            self.configure_settings(opts)

        extensions.registry.ready()

        # Dispatch to handler.
        self.pre_dispatch(opts)
        try:
            exit_code = self.dispatch_handler(opts)

        except Exception as ex:  # pylint: disable=broad-except
            self.dispatch_error(ex, opts)
            if not self.exception_report(ex, opts):
                raise

        except ApplicationExit as ex:
            if ex.message:
                print(f"\n\n{ex.message}", file=sys.stderr)
            raise

        except KeyboardInterrupt:
            print("\n\nInterrupted.", file=sys.stderr)
            sys.exit(2)

        else:
            # Provide exit code.
            self.post_dispatch(exit_code, opts)
            if exit_code:
                sys.exit(exit_code)

        finally:
            self.logging_shutdown()


CURRENT_APP: CliApplication | None = None


def _set_running_application(app: CliApplication):
    global CURRENT_APP  # noqa: PLW0603
    CURRENT_APP = app


def get_running_application() -> CliApplication:
    """Get the current running application instance."""
    return CURRENT_APP
