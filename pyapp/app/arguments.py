"""
Wrappers around argparse to provide a simplified interface
"""
import argparse

from typing import Callable, Optional, Union, Any, Sequence, Type


__all__ = ("Handler", "CommandProxy", "argument")


Handler = Callable[[argparse.Namespace], Optional[int]]


class CommandProxy:
    """
    Proxy object that wraps a handler.
    """

    def __init__(self, handler: Handler, sub_parser: argparse.ArgumentParser):
        """
        Initialise proxy

        :param handler: Callable object that accepts a single argument.

        """
        self.handler = handler
        self.sub_parser = sub_parser

        # Copy details
        self.__doc__ = handler.__doc__
        self.__name__ = handler.__name__
        self.__module__ = handler.__module__

        # Add any existing arguments
        if hasattr(handler, "arguments__"):
            for args, kwargs in handler.arguments__:
                self.add_argument(*args, **kwargs)
            del handler.arguments__

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """
        Add argument to proxy
        """
        self.sub_parser.add_argument(*args, **kwargs)

    def sub_command(
        self, handler: Handler = None, cli_name: str = None, doc: str = None
    ) -> "CommandProxy":
        """
        Decorator for registering handlers.

        :param handler: Handler function
        :param cli_name: Optional name to use for CLI; defaults to the
            function name.
        :param doc: Description for help; default is taken from the handlers doc string.

        """

        def inner(func: Handler) -> CommandProxy:
            name = cli_name or func.__name__

            # Setup sub parser
            description = doc or func.__doc__
            sub_parser = self.sub_parser.add_parser(
                name, help=description.strip() if description else None
            )

            # Create proxy instance
            proxy = CommandProxy(func, sub_parser)
            self._handlers[name] = proxy
            return proxy

        return inner(handler) if handler else inner


def argument(
    *name_or_flags,
    action: str = None,
    nargs: Union[int, str] = None,
    const: Any = None,
    default: Any = None,
    type: Type[Any] = None,
    choices: Sequence[Any] = None,
    required: bool = None,
    help: str = None,
    metavar: str = None,
    dest: str = None
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
    :param help: - A brief description of what the argument does.
    :param metavar: - A name for the argument in usage messages.
    :param dest: - The name of the attribute to be added to the object returned by parse_args().

    """
    kwargs = {
        "action": action,
        "nargs": nargs,
        "const": const,
        "default": default,
        "type": type,
        "choices": choices,
        "required": required,
        "help": help,
        "metavar": metavar,
        "dest": dest,
    }
    # Filter out none values
    kwargs = {key: value for key, value in kwargs.items() if value is not None}

    def wrapper(func: Union[Handler, CommandProxy]) -> Union[Handler, CommandProxy]:
        if isinstance(func, CommandProxy):
            func.add_argument(*name_or_flags, **kwargs)
        else:
            # Add the argument to a list that will be consumed by CommandProxy.
            if hasattr(func, "arguments__"):
                func.arguments__.insert(0, (name_or_flags, kwargs))
            else:
                func.arguments__ = [(name_or_flags, kwargs)]

        return func

    return wrapper
