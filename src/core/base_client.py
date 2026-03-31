"""
Base client class for all automation layers.
Provides common functionality like logging, configuration access, and retry logic.
"""

from typing import Any, Optional

from src.core.config_loader import ConfigLoader
from src.utils.logger import Logger


class BaseClient:
    """
    Abstract base class for all automation clients.
    
    Provides:
    - Logger instance
    - Configuration access
    - Common exception handling
    - Retry logic patterns
    
    Should be extended by specific implementations:
    - UIClient (Playwright)
    - APIClient (requests)
    - DatabaseClient (SQLAlchemy)
    - AWSClient (boto3)
    """

    def __init__(self, client_name: str = "BaseClient"):
        """
        Initialize base client.
        
        Args:
            client_name: Name of the client for logging
        """
        self._logger = Logger.get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._config = ConfigLoader.get_instance()
        self._client_name = client_name
        self._is_initialized = False

        self._logger.debug(f"Initializing {self._client_name}")

    @property
    def logger(self) -> Any:
        """Get logger instance."""
        return self._logger

    @property
    def config(self) -> ConfigLoader:
        """Get configuration loader."""
        return self._config

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._is_initialized

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def get_environment_config(self) -> dict[str, Any]:
        """Get environment-specific configuration."""
        return self._config.get_environment_config()

    def close(self) -> None:
        """
        Close client connection/resources.
        Should be overridden by subclasses.
        """
        self._logger.debug(f"Closing {self._client_name}")
        self._is_initialized = False

    def __repr__(self) -> str:
        """String representation of client."""
        return f"{self.__class__.__name__}(initialized={self._is_initialized})"

    def __enter__(self) -> "BaseClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
