"""
Enums and constants for the test automation framework.
"""

from enum import Enum


class AutomationType(Enum):
    """Supported automation types."""

    UI = "ui"
    API = "api"
    DATABASE = "database"
    AWS = "aws"
    HYBRID = "hybrid"


class BrowserType(Enum):
    """Supported browser types."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class EnvironmentType(Enum):
    """Supported test environments."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class LocatorStrategy(Enum):
    """Locator strategies for finding elements."""

    CSS = "css"
    XPATH = "xpath"
    ID = "id"
    NAME = "name"
    CLASS = "class"
    TAG = "tag"
    TEXT = "text"
    PLACEHOLDER = "placeholder"
    ARIA_LABEL = "aria-label"
    ROLE = "role"


class WaitStrategy(Enum):
    """Wait strategies for element interactions."""

    VISIBLE = "visible"
    HIDDEN = "hidden"
    ENABLED = "enabled"
    DISABLED = "disabled"
    STABLE = "stable"
    EDITABLE = "editable"


class LogLevel(Enum):
    """Log levels for logging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class HTTPMethod(Enum):
    """HTTP methods for API calls."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ContentType(Enum):
    """Content types for API requests/responses."""

    JSON = "application/json"
    XML = "application/xml"
    FORM = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain"
    HTML = "text/html"
