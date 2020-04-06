"""
Any command associated with a pyApp application can be expanded with arguments.
Arguments are a set of decorators that utilise ``argparse`` to simplify the
process of accepting and validating input/flags for commands.

.. autofunction:: argument

"""
import argparse
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

from pyapp.utils import cached_property

__all__ = ("Handler", "argument", "CommandGroup")


Handler = Callable[[argparse.Namespace], Optional[int]]


class ParserBase:
    """
    Base class for handling parsers.
    """

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser

    def argument(self, *name_or_flags, **kwargs):
        """
        Add argument to proxy
        """
        self.parser.add_argument(*name_or_flags, **kwargs)


class CommandProxy(Handler, ParserBase):
    """
    Proxy object that wraps a handler.
    """

    def __init__(self, handler: Handler, parser: argparse.ArgumentParser):
        """
        Initialise proxy

        :param handler: Callable object that accepts a single argument.

        """
        super().__init__(parser)
        self.handler = handler

        # Copy details
        self.__doc__ = handler.__doc__
        self.__name__ = handler.__name__
        self.__module__ = handler.__module__

        # Add any existing arguments
        if hasattr(handler, "arguments__"):
            for name_or_flags, kwargs in handler.arguments__:
                self.argument(*name_or_flags, **kwargs)
            del handler.arguments__

    def __call__(self, opts: argparse.Namespace):
        return self.handler(opts)


def argument(
    *name_or_flags,
    action: str = None,
    nargs: Union[int, str] = None,
    const: Any = None,
    default: Any = None,
    type: Type[Any] = None,  # pylint: disable=redefined-builtin
    choices: Sequence[Any] = None,
    required: bool = None,
    help_text: str = None,
    metavar: str = None,
    dest: str = None,
):
    """
    Decorator for adding arguments to a handler.

    This decorator can be used before or after the handler registration
    decorator :meth:`CliApplication.command` has been used.

    :param name_or_flags: - Either a name or a list of option strings, e.g. foo or -f, --foo.
    :param action: - The basic type of action to be taken when this argument is encountered at the command line.
    :param nargs: - The number of command-line arguments that should be consumed.
    :param const: - A constant value required by some action and nargs selections.
    :param default: - The value produced if the argument is absent from the command line.
    :param type: - The type to which the command-line argument should be converted.
    :param choices: - A container of the allowable values for the argument.
    :param required: - Whether or not the command-line option may be omitted (optionals only).
    :param help_text: - A brief description of what the argument does.
    :param metavar: - A name for the argument in usage messages.
    :param dest: - The name of the attribute to be added to the object returned by parse_args().

    """
    # Filter out None values
    kwargs = {
        "action": action,
        "nargs": nargs,
        "const": const,
        "default": default,
        "type": type,
        "choices": choices,
        "required": required,
        "help": help_text,
        "metavar": metavar,
        "dest": dest,
    }
    kwargs = {key: value for key, value in kwargs.items() if value is not None}

    def wrapper(func: Union[Handler, CommandProxy]) -> Union[Handler, CommandProxy]:
        if isinstance(func, CommandProxy):
            func.argument(*name_or_flags, **kwargs)
        else:
            # Add the argument to a list that will be consumed by CommandProxy.
            if hasattr(func, "arguments__"):
                func.arguments__.insert(0, (name_or_flags, kwargs))
            else:
                func.arguments__ = [(name_or_flags, kwargs)]

        return func

    return wrapper


class CommandGroup(ParserBase):
    """
    Group of commands.
    """

    def __init__(
        self,
        parser: argparse.ArgumentParser,
        _prefix: str = None,
        _handlers: Dict[str, Handler] = None,
    ):
        super().__init__(parser)
        self._prefix = _prefix
        self._handlers: Dict[str, Handler] = {} if _handlers is None else _handlers

        self._sub_parsers = parser.add_subparsers(dest=self.handler_dest)
        self._default_handler = self.default_handler

    @cached_property
    def handler_dest(self) -> str:
        """
        Destination of handler
        """
        return f":handler:{self._prefix or ''}"

    def _add_handler(self, handler, name, aliases):
        # Add proxy to handler list
        handler_name = f"{self._prefix}:{name}" if self._prefix else name
        self._handlers[handler_name] = handler

        # Add proxy to handler list
        for alias in aliases:
            handler_alias = f"{self._prefix}:{alias}" if self._prefix else alias
            self._handlers[handler_alias] = handler

    def create_command_group(
        self, name: str, *, aliases: Sequence[str] = (), help_text: str = None
    ) -> "CommandGroup":
        """
        Create a command group

        :param name: Name of the command group
        :param aliases: A sequence a name aliases for this command group.
        :param help_text: Information provided to the user if help is invoked.

        """
        kwargs = {"aliases": aliases}
        if help_text:
            kwargs["help"] = help_text
        group = CommandGroup(
            self._sub_parsers.add_parser(name, aliases=aliases, help=help_text),
            f"{self._prefix}:{name}" if self._prefix else name,
            self._handlers,
        )
        self._add_handler(group.dispatch_handler, name, aliases)

        return group

    def command(
        self,
        handler: Handler = None,
        *,
        name: str = None,
        aliases: Sequence[str] = (),
        help_text: str = None,
    ) -> CommandProxy:
        """
        Decorator for registering handlers.

        :param handler: Handler function
        :param name: Optional name to use for CLI; defaults to the function name.
        :param aliases: A sequence a name aliases for this command command.
        :param help_text: Information provided to the user if help is invoked;
            default is taken from the handlers doc string.

        """

        def inner(func: Handler) -> CommandProxy:
            kwargs = {"aliases": aliases}

            help_text_ = help_text or func.__doc__
            if help_text_:
                kwargs["help"] = help_text_.strip()

            name_ = name or func.__name__
            proxy = CommandProxy(func, self._sub_parsers.add_parser(name_, **kwargs))

            self._add_handler(proxy, name_, aliases)

            return proxy

        return inner(handler) if handler else inner

    def default(self, handler: Handler):
        """
        Decorator for registering a default handler.
        """
        self._default_handler = handler
        return handler

    def default_handler(self, _: argparse.Namespace) -> int:
        """
        Handler called if no handler is specified
        """
        print("No command specified!")
        self.parser.print_usage()
        return 1

    def dispatch_handler(self, opts: argparse.Namespace) -> int:
        """
        Resolve the correct handler and call it with supplied options namespace.
        """
        handler_name = getattr(opts, self.handler_dest, None)

        if self._prefix:
            handler_name = f"{self._prefix}:{handler_name}"
        handler = self._handlers.get(handler_name, self._default_handler)

        return handler(opts)
