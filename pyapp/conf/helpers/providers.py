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
Example::CheckMessage

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
from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import Generic
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from pyapp import checks
from pyapp.conf import settings
from pyapp.exceptions import ProviderNotFound
from pyapp.utils import cached_property
from pyapp.utils import import_type

__all__ = ("ProviderSummary", "ProviderFactoryBase")


ProviderSummary = namedtuple("ProviderSummary", ("code", "name", "description"))


PT = TypeVar("PT", covariant=True)


class ProviderFactoryBase(Generic[PT], metaclass=ABCMeta):
    """
    Factory to instantiate and configure a provider.
    """

    def __init__(self, setting: str, abc: Type[PT] = None):
        self.setting = setting
        self.abc = abc

        self._register_checks()

    def create(self, *args, **kwargs) -> PT:
        """
        Create a provider instance
        """
        provider_code, provider_config = self.load_config(*args, **kwargs)
        provider = self.get_provider(provider_code)
        return provider(**provider_config)

    @cached_property
    def providers(self) -> Dict[str, Any]:
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
    def provider_summaries(self) -> Sequence[ProviderSummary]:
        """
        Summary list of the available providers with code, name and description.

        This is intended for display purposes.
        """
        return tuple(
            ProviderSummary(
                code,
                getattr(provider, "name", provider.__name__),
                (provider.__doc__ or "").strip(),
            )
            for code, provider in self.providers.items()  # pylint: disable=no-member
        )

    def get_provider(self, provider_code: str) -> PT:
        """
        Get provider type from the supplied config.
        """
        try:
            return self.providers[provider_code]
        except KeyError:
            raise ProviderNotFound(
                f"Provider `{provider_code}` was not found in the provider list."
            )

    @abstractmethod
    def load_config(self, *args, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Load configuration for data store.

        This method should raise a ProviderConfigNotFound exception if configuration cannot be loaded
        """

    def _register_checks(self):
        checks.register(self)

    def checks(self, **kwargs):
        """
        Run checks to ensure settings are valid, secondly run checks against
        individual definitions in settings.

        """
        settings_ = kwargs["settings"]

        # Check settings are defined
        if not hasattr(settings_, self.setting):
            return checks.Critical(
                "Provider definitions missing from settings.",
                hint=f"Add a {self.setting} entry into settings.",
                obj=f"settings.{self.setting}",
            )

        provider_refs = getattr(settings_, self.setting)
        if provider_refs is None:
            return None  # Nothing is defined so end now.

        if not isinstance(provider_refs, (list, tuple)):
            return checks.Critical(
                "Provider definitions defined in settings not a list/tuple instance.",
                hint=f"Change setting {self.setting} to be a list or tuple in settings file.",
                obj=f"settings.{self.setting}",
            )

        messages = []

        for idx, provider_ref in enumerate(provider_refs):
            message = self.check_instance(idx, provider_ref, **kwargs)
            if isinstance(message, checks.CheckMessage):
                messages.append(message)
            elif message:
                messages.extend(message)

        return messages

    checks.check_name = "{obj.setting}.check_configuration"

    def check_instance(
        self, idx: int, provider_ref: str, **_
    ) -> Optional[Union["checks.CheckMessage", Sequence["checks.CheckMessage"]]]:
        """
        Checks for individual providers.
        """
        if not isinstance(provider_ref, str):
            return checks.Critical(
                "Provider definition is not a string.",
                hint="Change definition to be a string in settings.",
                obj=f"settings.{self.setting}[{idx}]",
            )

        try:
            import_type(provider_ref)
        except ImportError as ex:
            return checks.Critical(
                "Unable to import provider type.",
                hint=str(ex),
                obj=f"settings.{self.setting}[{idx}]",
            )

        return None
