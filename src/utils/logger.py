"""
Logger utility for the test automation framework.
Provides consistent logging across all layers.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.config_loader import ConfigLoader
from src.core.enums import LogLevel


class LoggerConfig:
    """Configuration for logger."""

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
        self.log_file: Optional[Path] = None
        self.format = "text"


class StructuredFormatter(logging.Formatter):
    """
    Structured logging formatter that can output JSON or text format.
    """

    def __init__(self, fmt: str = "text"):
        self.fmt = fmt
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.fmt == "json":
            return self._format_json(record)
        else:
            return self._format_text(record)

    @staticmethod
    def _format_json(record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

    @staticmethod
    def _format_text(record: logging.LogRecord) -> str:
        """Format log record as text."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f"[{timestamp}] [{record.levelname}] [{record.name}] "
            f"{record.module}.{record.funcName}:{record.lineno} - {record.getMessage()}"
        )

        if record.exc_info:
            msg += f"\n{logging.Formatter().formatException(record.exc_info)}"

        return msg


class Logger:
    """
    Singleton logger for test automation framework.
    Supports both file and console output with configurable format.
    """

    _loggers: dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: Optional[str] = None,
        config_loader: Optional[ConfigLoader] = None,
    ) -> logging.Logger:
        """
        Get or create logger instance.
        
        Args:
            name: Logger name (typically __name__)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            config_loader: ConfigLoader instance for reading config
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)

        # Get config
        if config_loader is None:
            config_loader = ConfigLoader.get_instance()

        log_config = config_loader.get_logging_config()
        config_level = level or log_config.get("level", "INFO")
        format_type = log_config.get("format", "text")
        log_file = log_config.get("file_path")
        console_output = log_config.get("console_output", True)

        # Set level
        try:
            logger.setLevel(getattr(logging, config_level.upper()))
        except AttributeError:
            logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter(fmt=format_type))
            logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(StructuredFormatter(fmt=format_type))
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def reset(cls) -> None:
        """Reset all loggers (useful for testing)."""
        cls._loggers.clear()
