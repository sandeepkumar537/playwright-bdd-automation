"""
Custom exceptions for the test automation framework.
Each layer has its own exception hierarchy for better error handling and loose coupling.
"""


class AutomationException(Exception):
    """Base exception for all automation framework errors."""

    pass


# UI Layer Exceptions
class UILayerException(AutomationException):
    """Base exception for UI automation layer."""

    pass


class ElementNotFoundError(UILayerException):
    """Raised when an element cannot be found on the page."""

    pass


class ElementNotVisibleError(UILayerException):
    """Raised when an element exists but is not visible for interaction."""

    pass


class ElementNotClickableError(UILayerException):
    """Raised when an element exists but cannot be clicked."""

    pass


class TimeoutError(UILayerException):
    """Raised when an operation times out (wait, navigation, etc.)."""

    pass


class BrowserError(UILayerException):
    """Raised when browser-related operations fail."""

    pass


class PageObjectError(UILayerException):
    """Raised when page object operations fail."""

    pass


class LocatorError(UILayerException):
    """Raised when locator operations fail."""

    pass


# API Layer Exceptions
class APILayerException(AutomationException):
    """Base exception for API automation layer."""

    pass


class APIConnectionError(APILayerException):
    """Raised when API connection fails."""

    pass


class APITimeoutError(APILayerException):
    """Raised when API request times out."""

    pass


class APIResponseError(APILayerException):
    """Raised when API response is invalid or unexpected."""

    pass


class APIAuthenticationError(APILayerException):
    """Raised when authentication to API fails."""

    pass


class APIValidationError(APILayerException):
    """Raised when API response validation fails."""

    pass


# Database Layer Exceptions
class DatabaseLayerException(AutomationException):
    """Base exception for database automation layer."""

    pass


class DatabaseConnectionError(DatabaseLayerException):
    """Raised when database connection fails."""

    pass


class DatabaseQueryError(DatabaseLayerException):
    """Raised when database query fails."""

    pass


class DatabaseTransactionError(DatabaseLayerException):
    """Raised when database transaction fails."""

    pass


class DatabaseTimeoutError(DatabaseLayerException):
    """Raised when database operation times out."""

    pass


# AWS Layer Exceptions
class AWSLayerException(AutomationException):
    """Base exception for AWS automation layer."""

    pass


class AWSConnectionError(AWSLayerException):
    """Raised when AWS connection fails."""

    pass


class AWSServiceError(AWSLayerException):
    """Raised when AWS service operation fails."""

    pass


class AWSAuthenticationError(AWSLayerException):
    """Raised when AWS authentication fails."""

    pass


class AWSTimeoutError(AWSLayerException):
    """Raised when AWS operation times out."""

    pass


# Configuration Exceptions
class ConfigurationException(AutomationException):
    """Base exception for configuration errors."""

    pass


class ConfigLoadError(ConfigurationException):
    """Raised when configuration cannot be loaded."""

    pass


class ConfigValidationError(ConfigurationException):
    """Raised when configuration validation fails."""

    pass


# Test Data Exceptions
class TestDataException(AutomationException):
    """Base exception for test data related errors."""

    pass


class TestDataValidationError(TestDataException):
    """Raised when test data validation fails."""

    pass


class TestDataFactoryError(TestDataException):
    """Raised when test data factory operation fails."""

    pass
