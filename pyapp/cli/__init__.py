"""
############################
Command Line Interface (CLI)
############################

"""
import argparse
try:
    import argcomplete
except ImportError:
    argcomplete = None

from pyapp import conf


def checks(opts):
    pass


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

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        self.sub_parser.add_argument(*args, **kwargs)
        return self


class CliApplication(object):
    """
    A CLI application object
    """
    def __init__(self, root_module, name=None, description=None, version=None):
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
                                     version or getattr(root_module, '__version__', 'Unknown')
                                 ))

        # Create sub parsers
        self.sub_parsers = self.parser.add_subparsers()

        self._handlers = {}
        self.register_builtin_handlers()

    def handler(self, handler=None, cli_name=None):
        """
        Register a handler

        :param handler:
        :param cli_name:

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
        handler = self.handler(checks)
        handler.add_argument('--tag', dest='tags', action='append')

    def dispatch(self):
        # Enable auto complete if available
        if argcomplete:
            argcomplete.autocomplete(self.parser)

        opts = self.parser.parse_args()


