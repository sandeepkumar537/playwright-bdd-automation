"""
Retry decorator and utilities for handling transient failures.
"""

import time
import random
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from src.framework.core.exceptions import AutomationException
from src.framework.utils.logger import Logger

# Type variable for decorated function
F = TypeVar("F", bound=Callable[..., Any])

logger = Logger.get_logger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_multiplier: float = 2.0,
        backoff_base: float = 1.0,
        jitter_enabled: bool = True,
        exceptions: tuple[Type[Exception], ...] = (Exception,),
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of attempts
            backoff_multiplier: Multiplier for exponential backoff
            backoff_base: Base delay for backoff (in seconds)
            jitter_enabled: Whether to add random jitter to delays
            exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.backoff_multiplier = backoff_multiplier
        self.backoff_base = backoff_base
        self.jitter_enabled = jitter_enabled
        self.exceptions = exceptions


def retry(config: Optional[RetryConfig] = None) -> Callable[[F], F]:
    """
    Retry decorator with exponential backoff.
    
    Args:
        config: RetryConfig instance. If None, uses defaults.
        
    Returns:
        Decorated function that retries on failure
        
    Example:
        @retry(RetryConfig(max_attempts=3, backoff_multiplier=2.0))
        def flaky_operation():
            # May fail occasionally
            return result
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exception = None

            while attempt < config.max_attempts:
                try:
                    attempt += 1
                    return func(*args, **kwargs)

                except config.exceptions as e:
                    last_exception = e
                    if attempt >= config.max_attempts:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = config.backoff_base * (config.backoff_multiplier ** (attempt - 1))

                    # Add jitter if enabled
                    if config.jitter_enabled:
                        delay += random.uniform(0, delay * 0.1)

                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}. "
                        f"Retrying in {delay:.2f}s: {str(e)}"
                    )
                    time.sleep(delay)

            # This should not happen due to exc_info above, but just in case
            if last_exception:
                raise last_exception

        return wrapper  # type: ignore

    return decorator


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Callable[[F], F]:
    """
    Convenient decorator for retry with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts (default 3)
        initial_delay: Initial delay between retries in seconds (default 1.0)
        backoff_factor: Multiplier for exponential backoff (default 2.0)
        
    Returns:
        Decorated function
        
    Example:
        @retry_with_backoff(max_attempts=5, initial_delay=2, backoff_factor=2)
        def unstable_operation():
            return result
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff_multiplier=backoff_factor,
        backoff_base=initial_delay,
        jitter_enabled=True,
    )
    return retry(config)
