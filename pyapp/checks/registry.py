"""
Checks Registry
~~~~~~~~~~~~~~~

Location for registering and listing checks.

"""
from itertools import chain
from typing import Callable
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Sequence
from typing import Union

from pyapp import extensions
from pyapp.checks.messages import CheckMessage
from pyapp.conf import Settings
from pyapp.conf import settings


class Tags:
    """
    Built-in tags used by pyApp.
    """

    security = "security"


Check = Callable[[Settings], Union[CheckMessage, Sequence[CheckMessage]]]


class CheckResult(NamedTuple):
    """
    Result of a check execution.
    """

    check: Check
    messages: Sequence[CheckMessage]


# TODO: Remove when pylint handles typing.List correctly  pylint: disable=fixme
# pylint: disable=not-an-iterable,no-member,unsupported-membership-test
class CheckRegistry(List[Check]):
    """
    Registry list for checks.
    """

    def register(
        self, check: Check = None, *tags
    ):  # pylint: disable=keyword-arg-before-vararg
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
registry = CheckRegistry()  # pylint: disable=invalid-name
register = registry.register  # pylint: disable=invalid-name
run_checks = registry.run_checks  # pylint: disable=invalid-name


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
