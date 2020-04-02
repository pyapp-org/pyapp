"""
Application
~~~~~~~~~~~

*Application with bindings for commands*

The application object handles all of the initial configuration to setup the
run-time environment.

Quick demo::

    >>> from pyapp.app import CliApplication, argument

    >>> app = CliApplication()

    >>> @argument('--verbose', target='verbose', action='store_true')
    >>> @app.command()
    >>> def hello(opts):
    ...     if opts.verbose:
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

Your application should have the following structure::

    my_app/__init__.py          # Include a __version__ variable
           __main__.py          # This is where the quick demo is located
           default_settings.py  # The default settings file
           checks.py            # Optional checks file


CliApplication
--------------

.. autoclass:: CliApplication
    :members: command, create_command_group, default, dispatch


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
import io
import logging.config
import os
import sys
from argparse import ArgumentParser
from argparse import Namespace as CommandOptions
from typing import Optional
from typing import Sequence

import argcomplete
import colorama

from .. import conf
from .. import extensions
from ..app import builtin_handlers
from ..injection import register_factory
from ..utils.inspect import import_root_module
from .argument_actions import *
from .arguments import *
from .logging_formatter import ColourFormatter

logger = logging.getLogger(__name__)


def _key_help(key: str) -> str:
    """
    Helper method that formats a key value from the environment vars
    """
    if key in os.environ:
        return f"{key} [{os.environ[key]}]"
    return key


class CliApplication(CommandGroup):
    """
    Application interface that provides a CLI interface.

    :param root_module: The root module for this application (used for discovery of other modules)
    :param prog: Name of your application; defaults to `sys.argv[0]`
    :param description: A description of your application for `--help`.
    :param version: Specify a specific version; defaults to `getattr(root_module, '__version__')`
    :param ext_white_list: Sequence if extensions that are white listed; default is `None` or all extensions.
    :param application_settings: The default settings for this application; defaults to `root_module.default_settings`
    :param application_checks: Location of application checks file; defaults to `root_module.checks` if it exists.
    :param env_settings_key: Key used to define settings file in environment.
    :param env_loglevel_key: Key used to define log level in environment

    """

    default_log_handler = logging.StreamHandler(sys.stderr)
    """
    Log handler applied by default to root logger.
    """

    default_log_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    """
    Log formatter applied by default to root logger handler.
    """

    default_color_log_formatter = ColourFormatter(
        f"{colorama.Fore.YELLOW}%(asctime)s{colorama.Fore.RESET} "
        f"%(clevelname)s "
        f"{colorama.Fore.LIGHTBLUE_EX}%(name)s{colorama.Fore.RESET} "
        f"%(message)s"
    )
    """
    Log formatter applied by default to root logger handler.
    """

    env_settings_key = conf.DEFAULT_ENV_KEY
    """
    Key used to define settings file in environment.
    """

    env_loglevel_key = "PYAPP_LOGLEVEL"
    """
    Key used to define log level in environment
    """

    additional_handlers = (
        builtin_handlers.checks,
        builtin_handlers.extensions,
        builtin_handlers.settings,
    )
    """
    Handlers to be added when builtin handlers are registered.
    """

    def __init__(
        self,
        root_module=None,
        *,
        prog: str = None,
        description: str = None,
        epilog: str = None,
        version: str = None,
        ext_white_list: Sequence[str] = None,
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
        self.ext_white_list = ext_white_list

        # Determine application settings
        if application_settings is None:
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

        self._init_parser()
        self.register_builtin_handlers()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<module {self.root_module.__name__}>)"

    def __str__(self) -> str:
        return self.application_summary

    @property
    def application_name(self) -> str:
        """
        Name of the application
        """
        return self.parser.prog

    @property
    def application_summary(self) -> str:
        """
        Summary of the application, name version and description.
        """
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
            "--nocolor",
            "--nocolour",
            dest="no_color",
            action="store_true",
            help="Disable colour output.",
        )
        self.argument(
            "--version",
            action="version",
            version=f"%(prog)s version: {self.application_version}",
        )

        # Log configuration
        self.argument(
            "--log-level",
            default=os.environ.get(self.env_loglevel_key, "INFO"),
            choices=("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"),
            help="Specify the log level to be used. "
            f"Defaults to env variable: {_key_help(self.env_loglevel_key)}",
        )
        self.argument(
            "--log-color",
            "--log-colour",
            dest="log_color",
            default=None,
            action="store_true",
            help="Force coloured output from logger (on console).",
        )
        self.argument(
            "--log-nocolor",
            "--log-nocolour",
            dest="log_color",
            action="store_false",
            help="Disable coloured output from logger (on console).",
        )

        # Global check values
        self.argument(
            "--checks",
            dest="checks_on_startup",
            action="store_true",
            help="Run checks on startup, any serious error will result "
            "in the application terminating.",
        )
        self.argument(
            "--checks-level",
            dest="checks_message_level",
            default="INFO",
            choices=("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"),
            help="Minimum level of check message to display",
        )

    def register_builtin_handlers(self):
        """
        Register any built in handlers.
        """
        # Register any additional handlers
        for additional_handler in self.additional_handlers:
            additional_handler(self)

    def pre_configure_logging(self):
        """
        Set some default logging so settings are logged.

        The main logging configuration from settings leaving us with a chicken
        and egg situation.

        """
        handler = self.default_log_handler
        handler.formatter = self.default_log_formatter

        # Apply handler to root logger and set level.
        logging.root.handlers = [handler]

    @staticmethod
    def register_factories():
        """
        Register any abstract interface factories.
        """
        # pylint: disable=import-outside-toplevel
        from asyncio import AbstractEventLoop, get_event_loop

        register_factory(AbstractEventLoop, get_event_loop)

    def load_extensions(self):
        """
        Load/Configure extensions.
        """
        entry_points = extensions.ExtensionEntryPoints(self.ext_white_list)
        extensions.registry.load_from(entry_points.extensions())
        extensions.registry.register_commands(self)

    def configure_settings(self, opts: CommandOptions):
        """
        Configure settings container.
        """
        application_settings = list(extensions.registry.default_settings)
        application_settings.append(self.application_settings)

        conf.settings.configure(
            application_settings, opts.settings, env_settings_key=self.env_settings_key
        )

    def get_log_formatter(self, log_color) -> logging.Formatter:
        """
        Get log formatter
        """
        log_handler = self.default_log_handler

        # Auto-detect colour mode
        if log_color is None:
            if isinstance(log_handler, logging.StreamHandler) and hasattr(
                log_handler.stream, "isatty"
            ):
                log_color = log_handler.stream.isatty()

        # Enable colour if specified.
        if log_color:
            return self.default_color_log_formatter

        return self.default_log_formatter

    def configure_logging(self, opts: CommandOptions):
        """
        Configure the logging framework.
        """
        self.default_log_handler.formatter = self.get_log_formatter(opts.log_color)

        if conf.settings.LOGGING:
            logger.info("Applying logging configuration.")

            # Set a default version if not supplied by settings
            dict_config = conf.settings.LOGGING.copy()
            dict_config.setdefault("version", 1)
            logging.config.dictConfig(dict_config)

        # Configure root log level
        logging.root.setLevel(opts.log_level)

    def checks_on_startup(self, opts: CommandOptions):
        """
        Run checks on startup.
        """
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
        """
        Generate a report for any unhandled exceptions caught by the framework.
        """
        logger.exception(
            "Un-handled exception %s caught executing handler: %s",
            exception,
            getattr(opts, self.handler_dest),
        )
        return False

    def dispatch(self, args: Sequence[str] = None) -> None:
        """
        Dispatch command to registered handler.
        """
        self.pre_configure_logging()
        self.register_factories()
        self.load_extensions()

        argcomplete.autocomplete(self.parser)
        opts = self.parser.parse_args(args)

        handler_name = getattr(opts, ":handler", None)
        if handler_name != "checks":
            self.configure_logging(opts)
            logger.info("Starting %s", self.application_summary)
            self.configure_settings(opts)
            self.checks_on_startup(opts)
        else:
            self.configure_settings(opts)

        _set_running_application(self)
        extensions.registry.ready()

        # Dispatch to handler.
        try:
            exit_code = self.dispatch_handler(opts)

        except Exception as ex:  # pylint: disable=broad-except
            if not self.exception_report(ex, opts):
                raise

        except KeyboardInterrupt:
            print("\n\nInterrupted.", file=sys.stderr)
            sys.exit(-2)

        else:
            # Provide exit code.
            if exit_code:
                sys.exit(exit_code)


CURRENT_APP: Optional[CliApplication] = None


def _set_running_application(app: CliApplication):
    global CURRENT_APP  # pylint: disable=global-statement
    CURRENT_APP = app


def get_running_application() -> CliApplication:
    """
    Get the current running application instance
    """
    return CURRENT_APP
