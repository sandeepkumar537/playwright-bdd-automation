"""
Retry decorator and utilities for handling transient failures.
"""

import time
import random
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from src.core.exceptions import AutomationException
from src.utils.logger import Logger

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


def retry_on_exception(
    max_attempts: int = 3,
    backoff_multiplier: float = 2.0,
    delay: float = 1.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """
    Simplified retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_multiplier: Exponential backoff multiplier
        delay: Initial delay between retries (seconds)
        exceptions: Exceptions to retry on
        
    Returns:
        Decorated function
        
    Example:
        @retry_on_exception(max_attempts=5, delay=2.0)
        def my_function():
            return result
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff_multiplier=backoff_multiplier,
        backoff_base=delay,
        jitter_enabled=True,
        exceptions=exceptions,
    )
    return retry(config)


def wait_with_retry(
    func: Callable[..., Any],
    max_attempts: int = 3,
    delay: float = 1.0,
) -> Any:
    """
    Execute function with retry logic.
    
    Args:
        func: Function to execute
        max_attempts: Maximum attempts
        delay: Delay between attempts
        
    Returns:
        Function result
    """

    @retry(
        RetryConfig(
            max_attempts=max_attempts,
            backoff_base=delay,
            backoff_multiplier=2.0,
            exceptions=(Exception,),
        )
    )
    def _internal() -> Any:
        return func()

    return _internal()
