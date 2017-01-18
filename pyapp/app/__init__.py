"""
*Application with bindings for commands*

Quick demo::

    >>> import my_app
    >>> from pyapp.app import CliApplication, add_argument
    >>> app = CliApplication(my_app)

    >>> @add_argument('--verbose', target='verbose', action='store_true')
    >>> @app.register_handler()
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

"""
from __future__ import print_function, absolute_import

import argparse
try:
    import argcomplete
except ImportError:
    argcomplete = None
import logging
import logging.config
import sys

from pyapp import conf
from pyapp.conf import settings


class HandlerProxy(object):
    """
    Proxy object that wraps a handler.
    """
    def __init__(self, handler, sub_parser):
        """
        Initialise proxy

        :param handler: Callable object that accepts a single argument.
        :type sub_parser: argparse.ArgumentParser

        """
        self.handler = handler
        self.sub_parser = sub_parser

        # Copy details
        self.__doc__ = handler.__doc__
        self.__name__ = handler.__name__
        self.__module__ = handler.__module__

        # Add any existing arguments
        if hasattr(handler, 'arguments'):
            for args, kwargs in handler.arguments:
                self.add_argument(*args, **kwargs)
            del handler.arguments

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """
        Add argument to proxy
        """
        self.sub_parser.add_argument(*args, **kwargs)
        return self


def add_argument(*args, **kwargs):
    """
    Decorator for adding arguments to a handler.

    This decorator can be used before or after the handler registration
    decorator :meth:`CliApplication.register_handler` has been used.

    """
    def wrapper(func):
        if isinstance(func, HandlerProxy):
            func.add_argument(*args, **kwargs)
        else:
            # Add the argument to a list that will be consumed by HandlerProxy.
            if not hasattr(func, 'arguments'):
                func.arguments = list()
            func.arguments.append((args, kwargs))
        return func
    return wrapper


class CliApplication(object):
    """
    :param root_module: The root module for this application (used for
        discovery of other modules)
    :param name: Name of your application; defaults to `sys.argv[0]`
    :param description: A description of your application for `--help`.
    :param version: Specify a specific version; defaults to
        `getattr(root_module, '__version__')`
    :param application_settings: The default settings for this application;
        defaults to `root_module.default_settings`

    """
    def __init__(self, root_module, name=None, description=None, version=None, 
                 application_settings=None):
        self.root_module = root_module
        self.name = name

        # Create argument parser
        self.parser = argparse.ArgumentParser(name, description=description)
        self.parser.add_argument('--settings', dest='settings',
                                 help='Settings to load; either a Python module or settings '
                                      'URL. Defaults to the env variable {}'.format(conf.DEFAULT_ENV_KEY))
        self.parser.add_argument('--log-level', dest='log_level', default='INFO',
                                 choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'))
        self.parser.add_argument('--version', action='version',
                                 version='%(prog)s version: {}'.format(
                                     version or getattr(root_module, '__version__', 'Unknown')))

        # Create sub parsers
        self.sub_parsers = self.parser.add_subparsers(dest='handler')

        self._handlers = {}
        self.register_builtin_handlers()

        # Determine application settings
        if application_settings is None:
            application_settings = '{}.default_settings'.format(root_module.__name__)
        self.application_settings = application_settings

    def register_handler(self, handler=None, cli_name=None):
        """
        Decorator for registering handlers.

        The description for help is taken from the handlers doc string.

        :param handler: Handler function
        :param cli_name: Optional name to use for CLI; defaults to the
            function name.
        :rtype: HandlerProxy

        """
        def inner(func):
            name = cli_name or func.__name__

            # Setup sub parser
            doc = func.__doc__
            sub_parser = self.sub_parsers.add_parser(
                name, help=doc.strip() if doc else None
            )

            # Create proxy instance
            proxy = HandlerProxy(func, sub_parser)
            self._handlers[name] = proxy
            return proxy

        return inner(handler) if handler else inner

    def register_builtin_handlers(self):
        """
        Register any built in handlers.
        """
        # Register the checks handler
        @add_argument('-t', '--tag', dest='tags', action='append',
                      help="Run checks associated with a tag.")
        @add_argument('-l', '--level', dest='message_level', default='INFO',
                      choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'))
        @add_argument('--verbose', dest='verbose', action='store_true',
                      help="Verbose output.")
        @add_argument('--nocolor', dest='no_color', action='store_true',
                      help="Disable colour output (if colorama is installed).")
        @add_argument('--out', dest='out', default=sys.stdout,
                      type=argparse.FileType(mode='w'),
                      help='File to output check report to; default is stdout.')
        def checks(opts):
            """
            Run a check report.
            """
            from pyapp.checks.report import CheckReport

            # Note the getLevelName method returns the level code if a string level is supplied!
            message_level = logging.getLevelName(opts.message_level)
            if CheckReport(opts.verbose, opts.no_color, opts.out).run(message_level, opts.tags):
                exit(4)

        self.register_handler(checks)

    def configure_settings(self, opts):
        """
        Configure settings container.
        """
        settings.configure(self.application_settings, opts.settings)

    def configure_logging(self, opts):
        """
        Configure the logging framework.
        """
        # Set a default version if not supplied by settings
        dict_config = settings.LOGGING.copy()
        dict_config.setdefault('version', 1)

        logging.config.dictConfig(dict_config)

        # Configure root log level
        logging.root.setLevel(opts.log_level)

    def dispatch(self, args=None):
        """
        Dispatch command to registered handler.
        """
        # Enable auto complete if available
        if argcomplete:
            argcomplete.autocomplete(self.parser)

        opts = self.parser.parse_args(args)

        self.configure_settings(opts)
        self.configure_logging(opts)

        # Dispatch to handler.
        try:
            self._handlers[opts.handler](opts)
        except Exception:
            # TODO: Generate an exception report.
            raise