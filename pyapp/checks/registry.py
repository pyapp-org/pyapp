from __future__ import absolute_import

from pyapp.conf import settings
from pyapp.utils import is_iterable

from .messages import CheckMessage


class Tags(object):
    """
    Built-in tags used by pyApp.
    """
    security = 'security'


class CheckRegistry(object):
    def __init__(self):
        self.registered_checks = []

    def register(self, check=None, *tags):
        """
        Can be used as a function or a decorator. Register given function
        `func` labeled with given `tags`. The function should receive **kwargs
        and return a list of Messages.

        Calling this method a second time allows for additional tags to be added.

        """
        def inner(func):
            func.tags = tags
            if func not in self.registered_checks:
                self.registered_checks.append(func)
            return func

        if callable(check):
            return inner(check)
        else:
            if check:
                tags += (check, )
            return inner

    def run_checks(self, tags=None):
        """
        Run all registered checks and return Messages. Use tags to filter checks.

        :param tags: Iterable of tags to filter checks by.

        """
        messages = []
        checks = list(self.registered_checks)

        if tags:
            # Filter the checks list
            checks = [check for check in checks
                      if hasattr(check, 'tags') and set(check.tags) & set(tags)]

        for check in checks:
            new_messages = check(settings=settings)
            if isinstance(new_messages, CheckMessage):
                messages.append(new_messages)
            elif is_iterable(new_messages):
                messages.extend(new_messages)

        return messages


# Singleton instance of registry
registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
