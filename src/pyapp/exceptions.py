"""
Exceptions
~~~~~~~~~~

Collection of standard exceptions.

"""
from typing import Optional


class ApplicationExit(SystemExit):
    """Exception used to directly exit a PyApp application.

    Will be caught by the CliApplication instance."""
    def __init__(self, status_code: int, message: Optional[str] = None):
        super().__init__(status_code)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        if self.message:
            return self.message
        return f"Application exit: {self.status_code}"


class InvalidConfiguration(Exception):
    """
    Invalid configuration was detected.
    """


class FactoryException(Exception):
    """
    Exceptions raised by factories
    """


class NotProvided(FactoryException, TypeError):
    """
    Definition in settings was not provided.
    """


class NotFound(FactoryException, KeyError):
    """
    The settings definition was not found.
    """


class CannotImport(FactoryException, ImportError):
    """
    The plugin defined in settings cannot be imported.
    """


class BadAlias(FactoryException, KeyError):
    """
    Alias is not configured correctly.
    """


class InvalidSubType(FactoryException, TypeError):
    """
    Instance type specified in settings does not match a subclass of the factory ABC
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


class EventException(Exception):
    """
    Exception caused by event/callback definition
    """


class UnsupportedObject(EventException, TypeError):
    """
    Instance does not have a dict that descriptor can use to store callbacks
    """
