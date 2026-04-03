"""
Base page object class for UI automation using Playwright.
Implements Page Object Model pattern with reusable interactions.
"""

from typing import Any, Optional

from playwright.async_api import Page, Locator
from playwright.sync_api import Page as SyncPage, Locator as SyncLocator

from src.framework.core.base_client import BaseClient
from src.framework.types.enums import LocatorStrategy, WaitStrategy
from src.framework.core.exceptions import (
    ElementNotFoundError,
    ElementNotVisibleError,
    TimeoutError as AutomationTimeoutError,
)


class BasePageObject(BaseClient):
    """
    Base class for page objects using Playwright.
    
    Provides:
    - Element finding with multiple locator strategies
    - Waiting for elements
    - Common interactions (click, fill, select, etc.)
    - Screenshot capture
    - Page navigation
    
    Usage:
        class LoginPage(BasePageObject):
            def __init__(self, page: Page):
                super().__init__("LoginPage")
                self.page = page
                
            def login(self, username: str, password: str):
                self.fill_text("username_field_locator", username)
                self.fill_text("password_field_locator", password)
                self.click("login_button_locator")
    """

    def __init__(self, page: Any, page_name: str = "BasePage"):
        """
        Initialize page object.
        
        Args:
            page: Playwright Page instance
            page_name: Name of the page for logging
        """
        super().__init__(client_name=page_name)
        self.page = page
        self._page_name = page_name
        self._is_initialized = True

    def find_element(
        self,
        locator: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> Any:
        """
        Find element using specified locator strategy.
        
        Args:
            locator: Locator string
            strategy: Locator strategy (CSS, XPATH, ID, etc.)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Locator object
            
        Raises:
            ElementNotFoundError: If element not found
        """
        try:
            if strategy == LocatorStrategy.XPATH:
                element = self.page.locator(f"xpath={locator}")
            elif strategy == LocatorStrategy.ID:
                element = self.page.locator(f"id={locator}")
            elif strategy == LocatorStrategy.CSS:
                element = self.page.locator(locator)
            elif strategy == LocatorStrategy.NAME:
                element = self.page.locator(f"[name='{locator}']")
            elif strategy == LocatorStrategy.PLACEHOLDER:
                element = self.page.locator(f"[placeholder='{locator}']")
            elif strategy == LocatorStrategy.ARIA_LABEL:
                element = self.page.locator(f"[aria-label='{locator}']")
            elif strategy == LocatorStrategy.TEXT:
                element = self.page.locator(f"text={locator}")
            elif strategy == LocatorStrategy.ROLE:
                # For role-based locators, format: "role=button[name='Click me']"
                element = self.page.locator(locator)
            else:
                element = self.page.locator(locator)

            # Verify element exists by waiting
            element.wait_for(timeout=timeout_ms, state="attached")
            self._logger.debug(f"Found element: {locator} using {strategy.value}")
            return element

        except Exception as e:
            self._logger.error(
                f"Failed to find element: {locator} using {strategy.value}: {str(e)}"
            )
            raise ElementNotFoundError(f"Element not found: {locator}") from e

    def wait_for_element(
        self,
        element: Any,
        state: WaitStrategy = WaitStrategy.VISIBLE,
        timeout_ms: int = 15000,
    ) -> None:
        """
        Wait for element to reach specified state.
        
        Args:
            element: Locator or element
            state: Wait state (visible, hidden, enabled, disabled, stable, editable)
            timeout_ms: Timeout in milliseconds
            
        Raises:
            TimeoutError: If timeout exceeded
        """
        try:
            state_value = state.value
            element.wait_for(timeout=timeout_ms, state=state_value)
            self._logger.debug(f"Element reached state: {state_value}")
        except Exception as e:
            self._logger.error(f"Timeout waiting for element state {state.value}: {str(e)}")
            raise AutomationTimeoutError(f"Element state timeout: {state.value}") from e

    def click(
        self,
        locator: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> None:
        """
        Click on element.
        
        Args:
            locator: Element locator
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms)
            self.wait_for_element(element, WaitStrategy.VISIBLE, timeout_ms)
            element.click()
            self._logger.debug(f"Clicked element: {locator}")
        except Exception as e:
            self._logger.error(f"Failed to click element {locator}: {str(e)}")
            raise

    def fill_text(
        self,
        locator: str,
        text: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> None:
        """
        Fill text input element.
        
        Args:
            locator: Element locator
            text: Text to fill
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms)
            self.wait_for_element(element, WaitStrategy.EDITABLE, timeout_ms)
            element.clear()
            element.fill(text)
            self._logger.debug(f"Filled text in element: {locator}")
        except Exception as e:
            self._logger.error(f"Failed to fill text in {locator}: {str(e)}")
            raise

    def get_text(
        self,
        locator: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> str:
        """
        Get text from element.
        
        Args:
            locator: Element locator
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Element text
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms)
            text = element.text_content()
            self._logger.debug(f"Got text from element: {locator} = {text}")
            return text or ""
        except Exception as e:
            self._logger.error(f"Failed to get text from {locator}: {str(e)}")
            raise

    def is_visible(
        self,
        locator: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 2000,
    ) -> bool:
        """
        Check if element is visible.
        
        Args:
            locator: Element locator
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
            
        Returns:
            True if visible, False otherwise
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms=100)
            return element.is_visible()
        except Exception:
            return False

    def is_enabled(
        self,
        locator: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> bool:
        """
        Check if element is enabled.
        
        Args:
            locator: Element locator
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
            
        Returns:
            True if enabled, False otherwise
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms)
            return element.is_enabled()
        except Exception:
            return False

    def select_option(
        self,
        locator: str,
        value: str,
        strategy: LocatorStrategy = LocatorStrategy.CSS,
        timeout_ms: int = 15000,
    ) -> None:
        """
        Select option from dropdown.
        
        Args:
            locator: Select element locator
            value: Value or label to select
            strategy: Locator strategy
            timeout_ms: Timeout in milliseconds
        """
        try:
            element = self.find_element(locator, strategy, timeout_ms)
            element.select_option(value)
            self._logger.debug(f"Selected option '{value}' in: {locator}")
        except Exception as e:
            self._logger.error(f"Failed to select option in {locator}: {str(e)}")
            raise

    def take_screenshot(self, filename: str) -> None:
        """
        Capture page screenshot.
        
        Args:
            filename: Filename for screenshot
        """
        try:
            self.page.screenshot(path=filename)
            self._logger.debug(f"Screenshot saved: {filename}")
        except Exception as e:
            self._logger.error(f"Failed to take screenshot: {str(e)}")

    def navigate_to(self, url: str, timeout_ms: int = 30000) -> None:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            timeout_ms: Timeout in milliseconds
        """
        try:
            self.page.goto(url, timeout=timeout_ms)
            self._logger.debug(f"Navigated to: {url}")
        except Exception as e:
            self._logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise

    def get_current_url(self) -> str:
        """
        Get current page URL.
        
        Returns:
            Current URL
        """
        return self.page.url

    def close(self) -> None:
        """Close page."""
        if self.page:
            self.page.close()
            self._logger.debug(f"Closed page: {self._page_name}")
        super().close()
