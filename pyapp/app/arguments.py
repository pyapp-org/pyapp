"""
Any command associated with a pyApp application can be expanded with arguments.
Arguments are a set of decorators that utilise ``argparse`` to simplify the
process of accepting and validating input/flags for commands.

.. autofunction:: argument

"""
import argparse
import asyncio
import inspect
from enum import Enum
from typing import _GenericAlias
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

from .argument_actions import EnumName
from .argument_actions import KeyValueAction
from pyapp.compatability import async_run
from pyapp.utils import cached_property

__all__ = ("Handler", "argument", "CommandGroup", "Arg")


Handler = Union[
    Callable[..., Optional[int]],
    Callable[[argparse.Namespace], Optional[int]],
    Callable[..., Awaitable[Optional[int]]],
    Callable[[argparse.Namespace], Awaitable[Optional[int]]],
]

EMPTY = inspect.Parameter.empty


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


class CommandProxy(ParserBase):
    """
    Proxy object that wraps a handler.

    .. versionupdated:: 4.4
        Determine arguments from handler signature.

    """

    __slots__ = ("__name__", "handler", "_args", "_require_namespace")

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
            for arg in handler.arguments__:
                arg.register_with_proxy(self)
            del handler.arguments__

        self._args = []
        self._require_namespace = False

        # Parse out any additional arguments
        self._extract_args(handler)

    def _extract_args(self, func):
        """
        Extract args from signature and turn into command line args
        """
        sig = inspect.signature(func)

        # Backwards compatibility
        if len(sig.parameters) == 1:
            ((name, parameter),) = sig.parameters.items()
            if (
                parameter.kind is parameter.POSITIONAL_OR_KEYWORD
                and parameter.annotation in (parameter.empty, argparse.Namespace)
            ):
                self._require_namespace = name
                return

        for name, parameter in sig.parameters.items():
            if parameter.annotation is argparse.Namespace:
                self._require_namespace = name
            else:
                Argument.from_parameter(name, parameter).register_with_proxy(self)
                self._args.append(name)

    def __call__(self, opts: argparse.Namespace):
        kwargs = {arg: getattr(opts, arg) for arg in self._args}
        if self._require_namespace:
            kwargs[self._require_namespace] = opts
        return self.handler(**kwargs)


class AsyncCommandProxy(CommandProxy):
    """
    Proxy object that wraps an async handler.

    Will handle starting a event loop.
    """

    def __call__(self, opts: argparse.Namespace):
        return async_run(super().__call__(opts))


class Argument:
    """
    Decorator for adding arguments to a handler.

    This decorator can be used before or after the handler registration
    decorator :meth:`CliApplication.command` has been used.

    :param name_or_flags: Either a name or a list of option strings, e.g. foo or -f, --foo.
    :param action: The basic type of action to be taken when this argument is encountered at the command line.
    :param nargs: The number of command-line arguments that should be consumed.
    :param const: A constant value required by some action and nargs selections.
    :param default: The value produced if the argument is absent from the command line.
    :param type: The type to which the command-line argument should be converted.
    :param choices: A container of the allowable values for the argument.
    :param required: Whether or not the command-line option may be omitted (optionals only).
    :param help_text: A brief description of what the argument does.
    :param metavar: A name for the argument in usage messages.
    :param dest: The name of the attribute to be added to the object returned by parse_args().

    """

    __slots__ = ("kwargs", "name_or_flags")

    @classmethod
    def arg(
        cls,
        *flags: str,
        default: Any = EMPTY,
        choices: Sequence[Any] = None,
        help: str = None,  # pylint: disable=redefined-builtin
        metavar: str = None,
    ) -> "Argument":
        """
        Aliased to become the inline definition for an argument

        :param flags: Additional flags to represent the entry (the name always comes from the field name)
        :param default: The value produced if the argument is absent from the command line.
        :param choices: A container of the allowable values for the argument.
        :param help: A brief description of what the argument does.
        :param metavar: - A name for the argument in usage messages.

        """
        return cls(
            *flags, default=default, choices=choices, help_text=help, metavar=metavar
        )

    @classmethod
    def from_parameter(cls, name: str, parameter: inspect.Parameter) -> "Argument":
        # pylint: disable=too-many-branches,too-many-statements
        """
        Generate an argument from a inspection parameter

        .. versionadded:: 4.4
            Determine arguments from handler signature.

        """
        positional = parameter.kind is not parameter.KEYWORD_ONLY
        type_ = parameter.annotation
        default = parameter.default
        flag = f"{'' if positional else '--'}{name.replace('_', '-')}"

        # If field is assigned an Argument use that as the starting point
        if isinstance(default, Argument):
            instance = default
            default = EMPTY
            instance.name_or_flags = (flag,) + instance.name_or_flags
        else:
            instance = cls(flag)

        # Start updating kwargs
        kwargs = instance.kwargs
        kwargs["dest"] = name
        if default is not EMPTY:
            kwargs.setdefault("default", default)

        # Handle type variances
        if isinstance(type_, type):
            if type_ is bool:
                type_ = None
                kwargs["action"] = "store_true"

            elif type_ is dict:
                type_ = None
                kwargs["action"] = KeyValueAction
                if positional:
                    kwargs["nargs"] = "+"

            elif type_ in (list, tuple):
                type_ = None
                kwargs["action"] = "append"
                if positional:
                    kwargs["nargs"] = "+"

            elif issubclass(type_, Enum):
                kwargs["action"] = EnumName

            elif not positional and "default" not in kwargs:
                kwargs["required"] = True

        elif isinstance(type_, argparse.FileType):
            # Just pass as this is an `argparse` builtin
            pass

        # Handle generic types
        elif type(type_) is _GenericAlias:  # pylint: disable=unidiomatic-typecheck
            generic_name = type_._name  # pylint: disable=protected-access

            if generic_name in ("Sequence", "List"):
                kwargs["action"] = "append"
                if positional:
                    kwargs["nargs"] = "+"

            elif generic_name in ("Mapping", "Dict"):
                kwargs["action"] = KeyValueAction
                if positional:
                    kwargs["nargs"] = "+"

            elif generic_name == "Tuple":
                kwargs["nargs"] = len(type_.__args__)

            else:
                raise RuntimeError("Unsupported generic type")

            type_ = type_.__args__[0] if type_.__args__ else None

        else:
            raise RuntimeError("Unsupported type")

        if type_:
            kwargs["type"] = type_

        return instance

    def __init__(
        self,
        *name_or_flags,
        action: str = None,
        nargs: Union[int, str] = None,
        const: Any = None,
        default: Any = EMPTY,
        type: Type[Any] = None,  # pylint: disable=redefined-builtin
        choices: Sequence[Any] = None,
        required: bool = None,
        help_text: str = None,
        metavar: str = None,
        dest: str = None,
    ):
        self.name_or_flags = name_or_flags

        # Filter out None values
        kwargs = (
            ("action", action),
            ("nargs", nargs),
            ("const", const),
            ("type", type),
            ("choices", choices),
            ("required", required),
            ("help", help_text),
            ("metavar", metavar),
            ("dest", dest),
        )
        self.kwargs = {key: val for key, val in kwargs if val is not None}
        if default is not EMPTY:
            self.kwargs["default"] = default

    def __call__(
        self, func: Union[Handler, CommandProxy]
    ) -> Union[Handler, CommandProxy]:
        if isinstance(func, CommandProxy):
            self.register_with_proxy(func)
        else:
            # Add the argument to a list that will be consumed by CommandProxy.
            if hasattr(func, "arguments__"):
                func.arguments__.insert(0, self)
            else:
                func.arguments__ = [self]

        return func

    def register_with_proxy(self, proxy: CommandProxy):
        """
        Register self with a command proxy
        """
        proxy.argument(*self.name_or_flags, **self.kwargs)


Arg = Argument.arg  # pylint: disable=invalid-name
argument = Argument  # pylint: disable=invalid-name


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

        .. versionchanged:: 4.3
            Async handlers supported.

        """

        def inner(func: Handler) -> CommandProxy:
            kwargs = {"aliases": aliases}

            help_text_ = help_text or func.__doc__
            if help_text_:
                kwargs["help"] = help_text_.strip()

            name_ = name or func.__name__
            if asyncio.iscoroutinefunction(func):
                proxy = AsyncCommandProxy(
                    func, self._sub_parsers.add_parser(name_, **kwargs)
                )
            else:
                proxy = CommandProxy(
                    func, self._sub_parsers.add_parser(name_, **kwargs)
                )

            self._add_handler(proxy, name_, aliases)

            return proxy

        return inner(handler) if handler else inner

    def default(self, handler: Handler):
        """
        Decorator for registering a default handler.

        .. versionchanged:: 4.3
            Async handlers supported.

        """
        if asyncio.iscoroutinefunction(handler):
            self._default_handler = AsyncCommandProxy(handler, self.parser)
        else:
            self._default_handler = CommandProxy(handler, self.parser)
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
