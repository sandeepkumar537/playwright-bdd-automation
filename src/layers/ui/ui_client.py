"""
UI Client - Manages browser and page lifecycle with Playwright.
"""

from typing import Any, Type, Optional, Dict

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from src.core.base_client import BaseClient
from src.core.enums import BrowserType
from src.core.exceptions import BrowserError
from src.utils.logger import Logger


class UIClient(BaseClient):
    """
    UI Client for managing Playwright browser sessions.
    
    Handles:
    - Browser initialization and teardown
    - Context management
    - Page creation and navigation
    - Browser configuration
    
    Usage:
        client = UIClient()
        client.start_browser()
        page = client.get_page()
        login_page = LoginPage(page)
        login_page.login("user", "pass")
        client.close_browser()
    """

    def __init__(self):
        """Initialize UI client."""
        super().__init__(client_name="UIClient")
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None
        self._pages: Dict[str, Page] = {}

    def start_browser(self) -> Page:
        """
        Start browser and create initial page.
        
        Returns:
            Initial Page object
            
        Raises:
            BrowserError: If browser fails to start
        """
        try:
            # Get browser configuration
            browser_config = self.config.get_browser_config()
            browser_type = browser_config.get("type", "chromium")
            headless = self.config.get("headless", False)
            viewport = browser_config.get("viewport", {"width": 1920, "height": 1080})
            locale = browser_config.get("locale", "en-US")
            timezone = browser_config.get("timezone", "UTC")

            # Initialize Playwright
            self._playwright = sync_playwright().start()

            # Get browser based on type
            if browser_type.lower() == "firefox":
                browser_launcher = self._playwright.firefox
            elif browser_type.lower() == "webkit":
                browser_launcher = self._playwright.webkit
            else:
                browser_launcher = self._playwright.chromium

            # Launch browser
            self.browser = browser_launcher.launch(headless=headless)
            self._logger.debug(f"Browser launched: {browser_type} (headless={headless})")

            # Create context with options
            self.context = self.browser.new_context(
                viewport=viewport,
                locale=locale,
                timezone_id=timezone
            )
            self._logger.debug(f"Browser context created: viewport={viewport}")

            # Create initial page
            self.page = self.context.new_page()
            self._is_initialized = True
            self._logger.debug("Initial page created")

            return self.page

        except Exception as e:
            self._logger.error(f"Failed to start browser: {str(e)}")
            raise BrowserError(f"Browser startup failed: {str(e)}") from e

    def get_page(self) -> Page:
        """
        Get current page or create new one if not exists.
        
        Returns:
            Current Page object
        """
        if self.page is None:
            raise BrowserError("Browser not started. Call start_browser() first.")
        return self.page

    def create_new_page(self) -> Page:
        """
        Create a new page in the same context.
        
        Returns:
            New Page object
            
        Raises:
            BrowserError: If context not initialized
        """
        if self.context is None:
            raise BrowserError("Browser context not initialized")

        page = self.context.new_page()
        self._pages[str(id(page))] = page
        self._logger.debug("New page created")
        return page

    def close_page(self, page: Optional[Page] = None) -> None:
        """
        Close a specific page.
        
        Args:
            page: Page to close. If None, closes current page.
        """
        page_to_close = page or self.page

        if page_to_close:
            page_to_close.close()
            self._logger.debug("Page closed")

            if page_to_close == self.page:
                self.page = None

    def close_browser(self) -> None:
        """Close browser and cleanup resources."""
        try:
            # Close all pages
            for page_id, page in list(self._pages.items()):
                try:
                    page.close()
                except Exception:
                    pass

            # Close current page
            if self.page:
                self.page.close()

            # Close context
            if self.context:
                self.context.close()
                self._logger.debug("Browser context closed")

            # Close browser
            if self.browser:
                self.browser.close()
                self._logger.debug("Browser closed")

            # Stop playwright
            if self._playwright:
                self._playwright.stop()
                self._logger.debug("Playwright stopped")

            self._is_initialized = False

        except Exception as e:
            self._logger.error(f"Error closing browser: {str(e)}")

    def maximize_window(self, width: int = 1920, height: int = 1080) -> None:
        """
        Maximize browser window.
        
        Args:
            width: Window width
            height: Window height
        """
        if self.page:
            self.page.set_viewport_size({"width": width, "height": height})
            self._logger.debug(f"Window resized to {width}x{height}")

    def get_browser_info(self) -> Dict[str, Any]:
        """Get browser information."""
        if not self.browser:
            return {}

        return {
            "browser_version": self.browser.version,
            "name": self.browser.browser_type.name,
        }

    def close(self) -> None:
        """Close browser (same as close_browser for compatibility)."""
        self.close_browser()
        super().close()
