from __future__ import unicode_literals


class InvalidConfiguration(Exception):
    """
    Invalid configuration was detected.
    """
    pass


class ProviderException(Exception):
    """
    Exceptions raised by providers.
    """


class ProviderNotFound(KeyError, ProviderException):
    """
    Specified provider not found.
    """


class ProviderConfigNotFound(ProviderException):
    """
    Specified provider configuration could not be loaded.
    """
