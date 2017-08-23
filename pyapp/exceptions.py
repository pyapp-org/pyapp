from __future__ import unicode_literals


class InvalidConfiguration(Exception):
    """
    Invalid configuration was detected.
    """
    pass


class ProviderException(Exception):
    pass


class ProviderNotFound(ProviderException):
    """
    Specified provider not found.
    """
