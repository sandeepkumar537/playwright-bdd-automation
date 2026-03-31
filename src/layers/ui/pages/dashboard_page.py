"""
Example Page Object - Dashboard Page.
Demonstrates advanced POM patterns with table components and navigation.
"""

from typing import List, Optional, Dict

from src.core.base_page import BasePageObject
from src.core.enums import LocatorStrategy
from src.layers.ui.locators.base_locator import Locator, BaseLocators
from src.layers.ui.components.ui_components import (
    ButtonComponent,
    TableComponent,
)


class DashboardPageLocators(BaseLocators):
    """Locators for Dashboard Page."""

    WELCOME_MESSAGE = Locator(LocatorStrategy.CSS, ".welcome-message")
    USER_MENU = Locator(LocatorStrategy.CSS, "[data-testid='user-menu']")
    LOGOUT_BUTTON = Locator(LocatorStrategy.CSS, "button[data-testid='logout']")
    USERS_TABLE = Locator(LocatorStrategy.CSS, "table.users-table")
    CREATE_USER_BUTTON = Locator(LocatorStrategy.CSS, "button[data-testid='create-user']")
    SEARCH_INPUT = Locator(LocatorStrategy.ID, "search-users")
    LOADING_SPINNER = Locator(LocatorStrategy.CSS, ".loading-spinner")

    # For less stable applications (IBM BAW), use XPath
    # USERS_TABLE = Locator(LocatorStrategy.XPATH, "//table[@role='grid']")
    # LOGOUT_BUTTON = Locator(LocatorStrategy.XPATH, "//a[contains(@href, '/logout')]")


class DashboardPage(BasePageObject):
    """
    Dashboard Page Object.
    
    Demonstrates:
    - Table component integration
    - Complex workflows
    - Reusable verification methods
    """

    def __init__(self, page):
        """
        Initialize Dashboard Page.
        
        Args:
            page: Playwright Page object
        """
        super().__init__(page, page_name="DashboardPage")

        # Initialize components
        self.logout_button = ButtonComponent(
            self, DashboardPageLocators.LOGOUT_BUTTON, "Logout Button"
        )
        self.create_user_button = ButtonComponent(
            self, DashboardPageLocators.CREATE_USER_BUTTON, "Create User Button"
        )
        self.users_table = TableComponent(
            self, DashboardPageLocators.USERS_TABLE, "Users Table"
        )

    def wait_for_dashboard_loaded(self, timeout_ms: int = 30000) -> None:
        """
        Wait for dashboard to load completely.
        
        Args:
            timeout_ms: Timeout in milliseconds
        """
        # Wait for main content (welcome message)
        element = self.find_element(
            DashboardPageLocators.WELCOME_MESSAGE.value,
            DashboardPageLocators.WELCOME_MESSAGE.strategy,
            timeout_ms,
        )
        self._logger.info("Dashboard loaded successfully")

    def wait_for_loading_complete(self, timeout_ms: int = 10000) -> None:
        """
        Wait for loading spinners to disappear.
        
        Args:
            timeout_ms: Timeout in milliseconds
        """
        # In Playwright, we can use page.wait_for_load_state()
        self.page.wait_for_load_state("networkidle", timeout=timeout_ms)
        self._logger.debug("Loading complete")

    def verify_welcome_message_visible(self, expected_username: Optional[str] = None) -> bool:
        """
        Verify welcome message is displayed.
        
        Args:
            expected_username: User name to check in welcome message
            
        Returns:
            True if welcome message visible
        """
        is_visible = self.is_visible(
            DashboardPageLocators.WELCOME_MESSAGE.value,
            DashboardPageLocators.WELCOME_MESSAGE.strategy,
        )

        if is_visible and expected_username:
            message = self.get_text(
                DashboardPageLocators.WELCOME_MESSAGE.value,
                DashboardPageLocators.WELCOME_MESSAGE.strategy,
            )
            return expected_username in message

        return is_visible

    def get_all_users(self) -> List[Dict[str, str]]:
        """
        Get all users from table.
        
        Returns:
            List of user dictionaries
        """
        return self.users_table.get_all_rows()

    def search_user(self, search_term: str) -> None:
        """
        Search for user in table.
        
        Args:
            search_term: Search term
        """
        self.fill_text(
            DashboardPageLocators.SEARCH_INPUT.value,
            search_term,
            DashboardPageLocators.SEARCH_INPUT.strategy,
        )
        self.wait_for_loading_complete()
        self._logger.info(f"Searched for user: {search_term}")

    def find_user_in_table(self, username: str) -> Optional[Dict[str, str]]:
        """
        Find specific user in table.
        
        Args:
            username: Username to find
            
        Returns:
            User data dictionary or None
        """
        # Search for user
        self.search_user(username)

        # Get all rows and find matching user
        users = self.get_all_users()

        for user in users:
            if user.get("Username") == username or user.get("username") == username:
                self._logger.info(f"Found user in table: {username}")
                return user

        self._logger.warning(f"User not found in table: {username}")
        return None

    def get_user_count(self) -> int:
        """
        Get total user count in table.
        
        Returns:
            Number of users
        """
        count = self.users_table.get_row_count()
        self._logger.debug(f"User count: {count}")
        return count

    def click_create_user(self) -> None:
        """Click create user button."""
        self.create_user_button.click()
        self._logger.info("Create User button clicked")

    def logout(self) -> None:
        """Perform logout."""
        self.logout_button.click()
        self._logger.info("Logged out successfully")

    def verify_table_loaded(self, timeout_ms: int = 15000) -> bool:
        """
        Verify users table is loaded.
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            True if table is visible
        """
        return self.is_visible(
            DashboardPageLocators.USERS_TABLE.value,
            DashboardPageLocators.USERS_TABLE.strategy,
            timeout_ms,
        )
