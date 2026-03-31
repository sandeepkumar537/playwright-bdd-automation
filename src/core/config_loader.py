"""
Configuration loader for managing test automation configuration.
Supports multiple environments and secrets management.
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from src.core.enums import EnvironmentType
from src.core.exceptions import ConfigLoadError, ConfigValidationError


class ConfigLoader:
    """
    Singleton configuration loader supporting TOML files and environment overrides.
    
    Configuration precedence:
    1. Environment variables (highest priority)
    2. secrets.toml (if exists)
    3. config.toml
    4. Default values (lowest priority)
    
    Usage:
        config = ConfigLoader.get_instance()
        base_url = config.get("base_url")
        db_host = config.get("database.host", "localhost")
    """

    _instance: Optional["ConfigLoader"] = None
    _config: dict[str, Any] = {}

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize config loader if not already done."""
        if self._initialized:
            return

        self._initialized = True
        self._load_configuration()

    @classmethod
    def get_instance(cls) -> "ConfigLoader":
        """Get singleton instance of ConfigLoader."""
        return cls()

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (useful for testing)."""
        cls._instance = None
        cls._config = {}

    def _load_configuration(self) -> None:
        """Load configuration from TOML files and environment variables."""
        try:
            # Load default config
            config_path = Path(__file__).parent.parent.parent / "config" / "config.toml"
            if config_path.exists():
                with open(config_path, "rb") as f:
                    self._config = tomllib.load(f)

            # Load secrets if available
            secrets_path = Path(__file__).parent.parent.parent / "config" / "secrets.toml"
            if secrets_path.exists():
                with open(secrets_path, "rb") as f:
                    secrets = tomllib.load(f)
                    self._merge_config(self._config, secrets)

            # Override with environment variables
            self._apply_env_overrides()

        except Exception as e:
            raise ConfigLoadError(f"Failed to load configuration: {str(e)}") from e

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Common environment variable mappings
        env_mappings = {
            "BASE_URL": "base_url",
            "API_BASE_URL": "api_base_url",
            "ENVIRONMENT": "environment",
            "BROWSER_TYPE": "browser.type",
            "HEADLESS": "headless",
            "DB_HOST": "database.host",
            "DB_PORT": "database.port",
            "DB_NAME": "database.name",
            "DB_USER": "database.user",
            "AWS_REGION": "aws.region",
        }

        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(self._config, config_key, env_value)

    def _set_nested_value(self, config: dict[str, Any], key_path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation."""
        keys = key_path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Path to config value (e.g., "database.host" or "base_url")
            default: Default value if not found
            
        Returns:
            Configuration value or default
            
        Example:
            base_url = config.get("base_url")
            db_host = config.get("database.host", "localhost")
        """
        keys = key_path.split(".")
        current = self._config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def get_environment(self) -> EnvironmentType:
        """Get current test environment."""
        env_str = self.get("environment", "dev").lower()
        try:
            return EnvironmentType(env_str)
        except ValueError:
            raise ConfigValidationError(
                f"Invalid environment: {env_str}. "
                f"Must be one of: {', '.join([e.value for e in EnvironmentType])}"
            )

    def get_environment_config(self, environment: Optional[str] = None) -> dict[str, Any]:
        """
        Get configuration for specific environment.
        
        Args:
            environment: Environment name (dev, staging, prod). 
                        If None, uses current environment from config.
            
        Returns:
            Environment-specific configuration dictionary
        """
        if environment is None:
            environment = self.get("environment", "dev")

        env_config = self.get(f"environment.{environment}", {})
        if not env_config:
            raise ConfigValidationError(f"Environment '{environment}' not found in configuration")

        return env_config

    def get_database_config(self, environment: Optional[str] = None) -> dict[str, Any]:
        """Get database configuration for environment."""
        env_config = self.get_environment_config(environment)
        return env_config.get("database", {})

    def get_aws_config(self, environment: Optional[str] = None) -> dict[str, Any]:
        """Get AWS configuration for environment."""
        env_config = self.get_environment_config(environment)
        return env_config.get("aws", {})

    def get_browser_config(self) -> dict[str, Any]:
        """Get browser configuration."""
        return self.get("browser", {})

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", {})

    def get_reporting_config(self) -> dict[str, Any]:
        """Get reporting configuration."""
        return self.get("reporting", {})

    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, raises ConfigValidationError otherwise
        """
        # Validate environment
        try:
            self.get_environment()
        except ConfigValidationError as e:
            raise e

        # Validate environment-specific config exists
        env = self.get("environment", "dev")
        try:
            self.get_environment_config(env)
        except ConfigValidationError as e:
            raise e

        return True

    @property
    def raw_config(self) -> dict[str, Any]:
        """Get raw configuration dictionary."""
        return self._config.copy()
