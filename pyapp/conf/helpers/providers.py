"""
*Dynamic configuration based Instance factories*

A provider is similar to a plugin in that they are created dynamically from
configuration. The main difference is that a providers configuration is
stored outside of settings. This could be in a database to provide user
specific endpoints eg fetching social media feeds.

This library provides the basic infrastructure for utilising providers.

This sample uses SQLAlchemy to access configuration data, it is assumed
that a config model has been created and that `provider_config` is a JSON
field.

Setup::

    >>> from pyapp.conf.helpers import ProviderFactoryBase
    >>> class FooProviderFactory(ProviderFactoryBase):
    ...     setting = 'MY_PROVIDERS'
    ...     def load_config(self, db_session, config_id):
    ...         try:
    ...             config = db_session.query(MyConfig).filter(MyConfig.id == config_id).one()
    ...         except NoResultFound:
    ...             raise ProviderConfigNotFound("Config not found for {}".format(config_id))
    ...         else:
    ...             return config.provider_ref, config.provider_config
    >>> foo_factory = FooProviderFactory()

Usage::

    >>> instance = foo_factory(db_session, 1)
Example::

    from pyapp.conf.helpers.providers import ProviderFactory

    class MyFooPlugin(

    class MyFooProvider(ProviderBase):
        name = 'Provides Foo!'



    class MyProviderFactory(ProviderFactoryBase):
        provider_list_setting = 'MY_PROVIDERS'

        def load_config(db_session, config_id):
            # Load configuration from database (using SQLAlchemy)
            try:
                config = db_session.query(MyProviderConfig).filter(MyProviderConfig.id == config_id).one()
            except NoResultFound:
                raise ProviderConfigNotFound("Config for not found for {}.".format(config_id))
            else:
                return config.provider_code, config.provider_config




"""
from __future__ import unicode_literals

from collections import namedtuple, OrderedDict

# Typing import
import six
from typing import Any, Dict, List, Tuple  # noqa

from pyapp import checks
from pyapp.conf import settings
from pyapp.exceptions import ProviderNotFound
from pyapp.utils import import_type, cached_property

__all__ = ('ProviderSummary', 'ProviderBase', 'ProviderFactoryBase')


ProviderSummary = namedtuple('ProviderSummary', ('code', 'name', 'description'))


class ProviderBase(object):
    """
    A specific provider type these are created by the provider factory, using stored
    configuration.
    """
    name = None
    """
    Providers name.
    """


class ProviderFactoryBase(object):
    """
    Factory to instantiate and configure a provider.
    """
    setting = None  # type: str
    """
    Setting that enumerates available providers.
    """

    abc = ProviderBase
    """
    The absolute base class that any provider should be based on.
    """

    def __init__(self):
        self._register_checks()

    def __call__(self, *args, **kwargs):
        provider_code, provider_config = self.load_config(*args, **kwargs)
        provider = self.get_provider(provider_code)
        return provider(**provider_config)

    @cached_property
    def providers(self):
        # type: () -> Dict[str, Any]
        """
        List of providers defined in settings.
        """
        providers = OrderedDict()

        # Load and instantiate available providers
        provider_refs = getattr(settings, self.setting)
        for provider_ref in provider_refs:
            providers[provider_ref] = import_type(provider_ref)

        return providers

    @cached_property
    def provider_summaries(self):
        # type: () -> List[ProviderSummary]
        """
        Summary list of the available providers with code, name and description.

        This is intended for display purposes.
        """
        return [
            ProviderSummary(code, provider.name, (provider.__doc__ or '').strip())
            for code, provider in self.providers.items()
        ]

    def get_provider(self, provider_code):
        # type: (str) -> Any
        """
        Get provider type from the supplied config.
        """
        try:
            return self.providers[provider_code]
        except KeyError:
            raise ProviderNotFound("Provider `{}` was not found in the provider list.".format(provider_code))

    def load_config(self, *args, **kwargs):
        # type: (*Any, **Any) -> Tuple[str, Dict[str, Any]]
        """
        Load configuration for data store.

        This method should raise a ProviderConfigNotFound exception if configuration cannot be loaded
        """
        raise NotImplementedError()

    def _register_checks(self):
        checks.register(self)

    def checks(self, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.

        """
        settings_ = kwargs['settings']

        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Provider definitions missing from settings.",
                hint="Add a {} entry into settings.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        provider_refs = getattr(settings_, self.setting)
        if provider_refs is None:
            return  # Nothing is defined so end now.

        if not isinstance(provider_refs, (list, tuple)):
            return checks.Critical(
                "Provider definitions defined in settings not a list/tuple instance.",
                hint="Change setting {} to be a list or tuple in settings file.".format(self.setting),
                obj="settings.{}".format(self.setting)
            )

        messages = []

        for idx, provider_ref in enumerate(provider_refs):
            message = self.check_instance(idx, provider_ref, **kwargs)
            if isinstance(message, checks.CheckMessage):
                messages.append(message)
            elif message:
                messages += message

        return messages
    checks.check_name = "{obj.setting}.check_configuration"

    def check_instance(self, idx, provider_ref, **_):
        """
        Checks for individual providers.
        """
        if not isinstance(provider_ref, six.string_types):
            return checks.Critical(
                "Provider definition is not a string.",
                hint="Change definition to be a string in settings.",
                obj='settings.{}[{}]'.format(self.setting, idx)
            )

        try:
            import_type(provider_ref)
        except ImportError as ex:
            return checks.Critical(
                "Unable to import provider type.",
                hint=str(ex),
                obj='settings.{}[{}]'.format(self.setting, idx)
            )
