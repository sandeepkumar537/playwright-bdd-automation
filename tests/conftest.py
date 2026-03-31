"""
Root Pytest Configuration and Hooks.
Central configuration for all tests.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.core.config_loader import ConfigLoader
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


def pytest_configure(config: pytest.Config) -> None:
    """
    Pytest hook - called before test session starts.
    
    Initializes:
    - Configuration loader
    - Logging
    - Custom markers
    
    Args:
        config: Pytest config object
    """
    logger.info("========== TEST SESSION STARTED ==========")
    
    # Load configuration
    try:
        config_loader = ConfigLoader.get_instance()
        config_loader.validate()
        environment = config_loader.get("environment", "dev")
        logger.info(f"Configuration loaded for environment: {environment}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise
    
    # Add custom markers
    config.addinivalue_line("markers", "ui: mark test as UI automation")
    config.addinivalue_line("markers", "api: mark test as API automation")
    config.addinivalue_line("markers", "database: mark test as database automation")
    config.addinivalue_line("markers", "aws: mark test as AWS automation")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """
    Pytest hook - called after test collection.
    
    Automatically adds markers based on test location/name.
    
    Args:
        config: Pytest config
        items: List of collected tests
    """
    for item in items:
        # Add markers based on file location
        if "features" in str(item.fspath):
            if "ui" in str(item.fspath):
                item.add_marker(pytest.mark.ui)
            elif "api" in str(item.fspath):
                item.add_marker(pytest.mark.api)
            elif "integration" in str(item.fspath):
                item.add_marker(pytest.mark.integration)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    Pytest hook - called for each test setup/call/teardown.
    
    Logs test start/end and handles failure screenshots.
    
    Args:
        item: Test item
        call: Call info
    """
    yield
    
    if call.when == "setup":
        logger.info(f"SETUP: {item.name}")
    
    elif call.when == "call":
        if call.excinfo is None:
            logger.info(f"PASSED: {item.name}")
        else:
            logger.error(f"FAILED: {item.name}")
            logger.error(f"Error: {call.excinfo.value}")
    
    elif call.when == "teardown":
        logger.info(f"TEARDOWN: {item.name}")


def pytest_sessionstart(session: pytest.Session) -> None:
    """
    Pytest hook - called before test session runs.
    
    Args:
        session: Pytest session
    """
    logger.info("Test session starting")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """
    Pytest hook - called after test session ends.
    
    Args:
        session: Pytest session
        exitstatus: Exit status code
    """
    logger.info(f"Test session finished with exit status: {exitstatus}")
    logger.info("========== TEST SESSION ENDED ==========")


# Import fixtures from src.fixtures.conftest
pytest_plugins = ["src.fixtures.conftest"]
