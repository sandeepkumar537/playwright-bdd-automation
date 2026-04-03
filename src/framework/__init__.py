"""
Framework - Core abstractions for test automation.

This module provides reusable base classes and utilities for building
multi-type test automation frameworks (UI, API, Database, AWS).
"""

# Core abstractions
from src.framework.core.base_client import BaseClient
from src.framework.core.base_page import BasePageObject
from src.framework.core.base_endpoint import BaseEndpoint
from src.framework.core.base_repository import BaseRepository
from src.framework.core.context import TestContext
from src.framework.core.config_loader import ConfigLoader
from src.framework.core.exceptions import (
    AutomationException,
    UILayerException,
    ElementNotFoundError,
    ElementNotVisibleError,
    APILayerException,
    DatabaseLayerException,
    AWSLayerException,
    ConfigurationException,
    ConfigLoadError,
)

# Types & Enums
from src.framework.types.enums import (
    AutomationType,
    BrowserType,
    EnvironmentType,
    LocatorStrategy,
    WaitStrategy,
    LogLevel,
    HTTPMethod,
    ContentType,
)

# Utilities
from src.framework.utils.logger import Logger
from src.framework.utils.retry import RetryConfig, retry, retry_with_backoff

__all__ = [
    # Core
    "BaseClient",
    "BasePageObject",
    "BaseEndpoint",
    "BaseRepository",
    "TestContext",
    "ConfigLoader",
    # Exceptions
    "AutomationException",
    "UILayerException",
    "ElementNotFoundError",
    "ElementNotVisibleError",
    "APILayerException",
    "DatabaseLayerException",
    "AWSLayerException",
    "ConfigurationException",
    "ConfigLoadError",
    # Types
    "AutomationType",
    "BrowserType",
    "EnvironmentType",
    "LocatorStrategy",
    "WaitStrategy",
    "LogLevel",
    "HTTPMethod",
    "ContentType",
    # Utils
    "Logger",
    "RetryConfig",
    "retry",
    "retry_with_backoff",
]
