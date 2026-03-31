"""
Test context class for managing test state across automation layers.
Enables loose coupling by providing a shared dictionary for test data.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TestContext:
    """
    Unified context for multi-type automation scenarios.
    
    This class holds references to all automation clients (UI, API, DB, AWS)
    and shared test data. It enables loose coupling between steps by providing
    a single point of state management.
    
    Attributes:
        test_data: Dictionary for sharing data between steps and layers
        ui_client: UI automation client (Playwright)
        api_client: API automation client (requests)
        db_client: Database client
        aws_client: AWS SDK client
        environment: Current test environment (dev, staging, prod)
        metadata: Test metadata (test name, timestamp, etc.)
    """

    test_data: dict[str, Any] = field(default_factory=dict)
    ui_client: Optional[Any] = None
    api_client: Optional[Any] = None
    db_client: Optional[Any] = None
    aws_client: Optional[Any] = None
    environment: str = "dev"
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_data(self, key: str, value: Any) -> None:
        """
        Add data to test context.
        
        Args:
            key: Data key
            value: Data value
        """
        self.test_data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from test context.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        return self.test_data.get(key, default)

    def remove_data(self, key: str) -> None:
        """Remove data from test context."""
        if key in self.test_data:
            del self.test_data[key]

    def clear_data(self) -> None:
        """Clear all test data."""
        self.test_data.clear()

    def set_metadata(self, key: str, value: Any) -> None:
        """Add metadata."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata."""
        return self.metadata.get(key, default)
