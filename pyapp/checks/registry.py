from __future__ import absolute_import, unicode_literals

from itertools import chain

from pyapp import extensions
from pyapp.conf import settings
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
            setattr(func, '_check__tags', tags)
            if func not in self.registered_checks:
                self.registered_checks.append(func)
            return func

        if callable(check) or hasattr(check, 'checks'):
            return inner(check)
        else:
            if check:
                tags += (check, )
            return inner

    def checks_by_tags(self, tags=None):
        """
        Return an iterator of checks that relate to a specific tag (or tags)
        """
        checks = self.registered_checks

        if tags:
            tags = set(tags)
            return (check for check in checks
                    if set(getattr(check, '_check__tags', [])) & tags)
        else:
            return iter(checks)

    def run_checks_iter(self, tags=None, pre_callback=None): 
        """
        Iterate through all registered checks and run each to return messages.

        :param tags: Iterable of tags to filter checks by.
        :param pre_callback: Callback triggered before each check is executed.

        """
        check_kwargs = {'settings': settings}

        for check in self.checks_by_tags(tags):
            if pre_callback:
                pre_callback(check)

            # Detect attached checks (or a class with checks)
            if hasattr(check, 'checks'):
                messages = check.checks(**check_kwargs)
            else:
                messages = check(**check_kwargs)

            if isinstance(messages, CheckMessage):
                yield messages,  # yield tuple, comma is expected
            elif messages:
                yield messages
            else:
                yield tuple()  # empty tuple a value should be yielded for each check

    def run_checks(self, tags=None):
        """
        Run all registered checks and return Messages. Use tags to filter checks.

        :param tags: Iterable of tags to filter checks by.

        """
        return list(chain.from_iterable(self.run_checks_iter(tags)))


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
