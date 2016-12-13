"""
#########################################
Application with bindings for application
#########################################

"""
from __future__ import print_function

import argparse
try:
    import argcomplete
except ImportError:
    argcomplete = None
import functools
import logging
import logging.config

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
        if hasattr(handler, '_add_arguments'):
            for args, kwargs in handler._add_arguments:
                self.add_argument(*args, **kwargs)
            del handler._add_arguments

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """
        Add argument to proxy
        """
        self.sub_parser.add_argument(*args, **kwargs)
        return self


def add_argument(*args, **kwargs):
    def wrapper(func):
        if isinstance(func, HandlerProxy):
            func.add_argument(*args, **kwargs)

        else:
            if not hasattr(func, '_add_arguments'):
                func._add_arguments = list()
            func._add_arguments.append((args, kwargs))
        return func
    return wrapper


class CliApplication(object):
    """
    A CLI application.
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

        # Determine application settings
        if application_settings is None:
            application_settings = '{}.default_settings'.format(root_module.__name__)
        self.application_settings = application_settings

        self._handlers = {}
        self.register_builtin_handlers()

    def handler(self, handler=None, cli_name=None):
        """
        Register a handler

        :param handler:
        :param cli_name:
        :rtype: HandlerProxy

        """
        def inner(func):
            name = cli_name or func.__name__

            # Setup sub parser
            doc = handler.__doc__
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
        Register any built in handlers
        """
        # Register the checks handler
        @self.handler
        @add_argument('--tags', dest='tags')
        def checks(opts):
            """
            Execute checks
            """
            from pyapp.checks.report import CheckReport

            messages = CheckReport(opts.verbose).run(opts.tags)
            if any(message.is_serious() for message in messages):
                exit(2)
        checks.add_argument('--tag', dest='tags', action='append',
                            help="Run checks associated with a tags.")
        checks.add_argument('--verbose', dest='verbose', action='store_true',
                            help="Verbose output")
        checks.add_argument('--no-color', dest='no_color', action='store_true',
                            help="Disable colour output.")

    def configure_settings(self, opts):
        """
        Configure settings
        """
        settings.configure(self.application_settings, opts.settings)

    def configure_logging(self):
        """
        Configure the logging framework
        """
        dict_config = settings.LOGGING.copy()
        dict_config.setdefault('version', 1)
        logging.config.dictConfig(dict_config)

    def dispatch(self):
        """
        Dispatch to correct application.
        """
        # Enable auto complete if available
        if argcomplete:
            argcomplete.autocomplete(self.parser)

        opts = self.parser.parse_args()

        self.configure_settings(opts)
        self.configure_logging()

        # Dispatch to handler instance.
        try:
            handler = self._handlers[opts.handler]
        except KeyError:
            exit(2)
        else:
            handler(opts)
