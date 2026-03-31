"""
Locator class for UI element identification.
Supports multiple strategies for finding elements across different applications.
"""

from dataclasses import dataclass
from enum import Enum

from src.core.enums import LocatorStrategy


@dataclass
class Locator:
    """
    Represents a UI element locator with strategy and value.
    
    Supports multiple locator strategies to work with different applications:
    - CSS selectors
    - XPath expressions (for complex element selection)
    - Element IDs (when stable)
    - Accessibility attributes (aria-label, role)
    - Text-based matching
    
    Usage:
        # Simple ID locator
        username_field = Locator(LocatorStrategy.ID, "username")
        
        # XPath for complex scenarios (IBM BAW where IDs may be volatile)
        user_menu = Locator(LocatorStrategy.XPATH, "//button[@data-test='user-menu']")
        
        # Accessibility-based (recommended for accessibility)
        submit_button = Locator(LocatorStrategy.ROLE, "button[name='Submit']")
    """

    strategy: LocatorStrategy
    value: str
    
    def __init__(self, strategy: LocatorStrategy, value: str):
        """
        Initialize Locator.
        
        Args:
            strategy: Locator strategy (CSS, XPATH, ID, NAME, ARIA_LABEL, etc.)
            value: Locator value specific to the strategy
        """
        self.strategy = strategy
        self.value = value

    def __str__(self) -> str:
        """String representation of locator."""
        return f"{self.strategy.value}:{self.value}"

    def to_playwright_locator(self) -> str:
        """
        Convert to Playwright locator format.
        
        Returns:
            Playwright locator string
        """
        if self.strategy == LocatorStrategy.CSS:
            return self.value
        elif self.strategy == LocatorStrategy.XPATH:
            return f"xpath={self.value}"
        elif self.strategy == LocatorStrategy.ID:
            return f"id={self.value}"
        elif self.strategy == LocatorStrategy.NAME:
            return f"[name='{self.value}']"
        elif self.strategy == LocatorStrategy.PLACEHOLDER:
            return f"[placeholder='{self.value}']"
        elif self.strategy == LocatorStrategy.ARIA_LABEL:
            return f"[aria-label='{self.value}']"
        elif self.strategy == LocatorStrategy.TEXT:
            return f"text={self.value}"
        elif self.strategy == LocatorStrategy.ROLE:
            return self.value  # Already in role format
        else:
            return self.value


class BaseLocators:
    """
    Base class for organizing locators.
    Extend this for app-specific locator collections.
    
    Usage:
        class LoginPageLocators(BaseLocators):
            USERNAME = Locator(LocatorStrategy.ID, "username")
            PASSWORD = Locator(LocatorStrategy.ID, "password")
            LOGIN_BUTTON = Locator(LocatorStrategy.CSS, "button.login-btn")
    """

    pass
