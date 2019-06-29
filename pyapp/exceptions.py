class InvalidConfiguration(Exception):
    """
    Invalid configuration was detected.
    """


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


class UnsupportedContentType(Exception):
    """
    Content type of the file is not supported
    """
