"""
Pytest Fixtures - Dependency Injection for Test Automation.
Provides shared fixtures for all tests with proper setup/teardown.
"""

import pytest
from typing import Generator

from src.core.context import TestContext
from src.core.config_loader import ConfigLoader
from src.layers.ui.ui_client import UIClient
from src.layers.api.api_client import APIClient
from src.layers.database.database_client import DatabaseClient
from src.layers.aws.aws_client import AWSClient
from src.services.user_service import UserService
from src.utils.logger import Logger


# Configure logger
logger = Logger.get_logger(__name__)


@pytest.fixture(scope="session")
def config_loader() -> ConfigLoader:
    """
    Session-scoped config loader.
    Loads configuration once per test session.
    
    Returns:
        ConfigLoader instance
    """
    logger.info("Loading configuration")
    config = ConfigLoader.get_instance()
    config.validate()
    return config


@pytest.fixture(scope="function")
def test_context() -> Generator[TestContext, None, None]:
    """
    Function-scoped test context.
    Created fresh for each test to ensure test isolation.
    
    Yields:
        TestContext instance for current test
    """
    context = TestContext()
    context.environment = ConfigLoader.get_instance().get("environment", "dev")
    
    logger.debug(f"Created test context for environment: {context.environment}")
    
    yield context
    
    # Cleanup
    context.clear_data()
    logger.debug("Cleaned up test context")


@pytest.fixture(scope="function")
def ui_client(test_context: TestContext) -> Generator[UIClient, None, None]:
    """
    Function-scoped UI client with browser.
    
    Creates a new browser session for each test.
    
    Args:
        test_context: Test context fixture
        
    Yields:
        UIClient instance with initialized browser
    """
    logger.info("Starting browser")
    
    client = UIClient()
    client.start_browser()
    test_context.ui_client = client
    
    yield client
    
    # Cleanup
    logger.info("Closing browser")
    client.close_browser()
    test_context.ui_client = None


@pytest.fixture(scope="function")
def api_client(test_context: TestContext, config_loader: ConfigLoader) -> Generator[APIClient, None, None]:
    """
    Function-scoped API client.
    
    Creates a new API session for each test.
    
    Args:
        test_context: Test context fixture
        config_loader: Config loader fixture
        
    Yields:
        APIClient instance
    """
    logger.info("Initializing API client")
    
    base_url = config_loader.get("api_base_url")
    client = APIClient(base_url=base_url)
    test_context.api_client = client
    
    yield client
    
    # Cleanup
    logger.info("Closing API client")
    client.close()
    test_context.api_client = None


@pytest.fixture(scope="function")
def db_client(test_context: TestContext, config_loader: ConfigLoader) -> Generator[DatabaseClient, None, None]:
    """
    Function-scoped database client.
    
    Creates a new database connection for each test.
    
    Args:
        test_context: Test context fixture
        config_loader: Config loader fixture
        
    Yields:
        DatabaseClient instance
    """
    logger.info("Initializing database client")
    
    client = DatabaseClient()
    
    # Get database config from environment
    db_config = config_loader.get_environment_config().get("database", {})
    
    try:
        client.connect(**db_config)
        test_context.db_client = client
        
        yield client
        
    finally:
        # Cleanup
        logger.info("Closing database client")
        if client.is_connected():
            client.close()
        test_context.db_client = None


@pytest.fixture(scope="function")
def aws_client(test_context: TestContext, config_loader: ConfigLoader) -> Generator[AWSClient, None, None]:
    """
    Function-scoped AWS client.
    
    Creates a new AWS session for each test.
    
    Args:
        test_context: Test context fixture
        config_loader: Config loader fixture
        
    Yields:
        AWSClient instance
    """
    logger.info("Initializing AWS client")
    
    client = AWSClient()
    
    # Get AWS config from environment
    aws_config = config_loader.get_aws_config()
    
    try:
        client.connect(**aws_config)
        test_context.aws_client = client
        
        yield client
        
    finally:
        # Cleanup
        logger.info("Closing AWS client")
        if client.is_connected():
            client.close()
        test_context.aws_client = None


@pytest.fixture(scope="function")
def user_service(test_context: TestContext) -> UserService:
    """
    User Service fixture for business logic orchestration.
    
    Args:
        test_context: Test context with all clients
        
    Returns:
        UserService instance
    """
    return UserService(test_context)


# Parametrized fixtures for multi-environment testing

@pytest.fixture(scope="session", params=["dev", "staging"])
def multi_environment(request) -> str:
    """
    Parametrized environment fixture.
    Runs test on multiple environments.
    
    Usage:
        def test_login(ui_client, multi_environment):
            # Test will run on dev and staging
            pass
    
    Args:
        request: Pytest request object
        
    Returns:
        Environment name
    """
    return request.param
