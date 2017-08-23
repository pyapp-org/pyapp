"""
Providers
~~~~~~~~~

A provider is similar to a plugin in that they are created dynamically from
configuration. The main difference is that a providers configuration is
stored outside of settings. This could be in a database to provide user
specific endpoints (eg fetching social media feeds).

"""
from collections import namedtuple, OrderedDict

# Typing import
from typing import Any, Dict, List  # noqa

from pyapp.conf import settings
from pyapp.exceptions import ProviderNotFound
from pyapp.utils import import_type, cached_property

ProviderSummary = namedtuple('ProviderSummary', ('code', 'name', 'description'))


class ProviderFactory(object):
    """
    Factory to instantiate and configure a provider.
    """

    def __init__(self, provider_list_setting=None, provider_base=None):
        # type: (str, Any) -> None
        """
        Initialise factory.

        :param provider_list_setting: Setting that lists available providers.
        :param provider_base: A base class the providers must inherit from.

        """
        self.provider_list_setting = provider_list_setting
        self.provider_base = provider_base

    @cached_property
    def providers(self):
        # type: () -> Dict[str, Any]
        """
        List of providers defined in settings.
        """
        providers = OrderedDict()

        # Load and instantiate available providers
        provider_refs = getattr(settings, self.provider_list_setting)
        for provider_ref in provider_refs:
            provider = import_type(provider_ref)
            providers[provider_ref] = self.instantiate_provider(provider)

        return providers

    @cached_property
    def provider_summary(self):
        # type: () -> List[ProviderSummary]
        """
        Summary list of the available providers with code, name and description.

        This is intended for display purposes.
        """
        return [
            ProviderSummary(code, provider.name, provider.__doc__)
            for code, provider in self.providers.items()
        ]

    def instantiate_provider(self, provider):
        # type: (type) -> Any
        """
        Create a provider instance.

        Can be overridden if your solution requires more parameters.
        """
        return provider()

    def get_provider(self, provider_code):
        # type: (str) -> Any
        """
        Get provider instance from the supplied config.
        """
        try:
            return self.providers[provider_code]
        except KeyError:
            raise ProviderNotFound("Provider `{}` was not found in the provider list.".format(provider_code))

    def __call__(self, *args, **kwargs):
        pass


class ProviderBase(object):
    """
    A specific provider type, this is a singleton instance that is used to define
    information about the provider, including which configuration variables and
    or any other special information about how a provider is instantiated and executed.
    """
    name = None
    """
    Providers name.
    """
