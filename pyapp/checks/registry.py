from itertools import chain
from typing import Iterable, Sequence, NamedTuple, Union, Callable

from pyapp import extensions
from pyapp.conf import settings, Settings
from .messages import CheckMessage


class Tags:
    """
    Built-in tags used by pyApp.
    """

    security = "security"


Check = Callable[[Settings], Union[CheckMessage, Sequence[CheckMessage]]]


class CheckResult(NamedTuple):
    check: Check
    messages: Sequence[CheckMessage]


class CheckRegistry(list):
    def register(self, check: Check = None, *tags):
        """
        Can be used as a function or a decorator. Register given function
        `func` labeled with given `tags`. The function should receive **kwargs
        and return a list of Messages.

        Calling this method a second time allows for additional tags to be added.

        """

        def inner(func):
            setattr(func, "_check__tags", tags)
            if func not in self:
                self.append(func)
            return func

        if callable(check) or hasattr(check, "checks"):
            return inner(check)
        else:
            if check:
                tags += (check,)
            return inner

    def checks_by_tags(self, tags: Iterable[str] = None):
        """
        Return an iterator of checks that relate to a specific tag (or tags)
        """
        if tags:
            tags = set(tags)
            return (
                check
                for check in self
                if set(getattr(check, "_check__tags", [])) & tags
            )
        else:
            return iter(self)

    def run_checks_iter(self, tags: Iterable[str] = None, pre_callback=None):
        """
        Iterate through all registered checks and run each to return messages.

        :param tags: Iterable of tags to filter checks by.
        :param pre_callback: Callback triggered before each check is executed.

        """
        check_kwargs = {"settings": settings}

        for check in self.checks_by_tags(tags):
            if pre_callback:
                pre_callback(check)

            # Detect attached checks (or a class with checks)
            if hasattr(check, "checks"):
                messages = check.checks(**check_kwargs)
            else:
                messages = check(**check_kwargs)

            if isinstance(messages, CheckMessage):
                yield CheckResult(check, (messages,))
            elif messages:
                yield CheckResult(check, messages)
            else:
                yield CheckResult(check, tuple())

    def run_checks(self, tags: Iterable[str] = None) -> Sequence[CheckMessage]:
        """
        Run all registered checks and return Messages. Use tags to filter checks.

        :param tags: Iterable of tags to filter checks by.

        """
        return tuple(
            chain.from_iterable(r.messages for r in self.run_checks_iter(tags))
        )


# Singleton instance of registry
registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks


def import_checks():
    """
    Import all of the modules defined in the setting `CHECK_LOCATIONS` and any checks
    defined by extensions.

    By importing the modules this ensures that checks are registered.
    """
    for location in settings.CHECK_LOCATIONS:
        __import__(location)

    for location in extensions.registry.check_locations:
        __import__(location)
