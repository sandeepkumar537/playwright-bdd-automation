"""
Example Page Object - Login Page.
Demonstrates how to create pages using POM pattern with components.
"""

from typing import Optional

from src.core.base_page import BasePageObject
from src.core.enums import LocatorStrategy
from src.layers.ui.locators.base_locator import Locator, BaseLocators
from src.layers.ui.components.ui_components import (
    TextInputComponent,
    ButtonComponent,
)


class LoginPageLocators(BaseLocators):
    """Locators for Login Page - customize based on your application."""

    # These are example locators. Adjust strategies and values for your app.
    USERNAME_FIELD = Locator(LocatorStrategy.ID, "username")
    PASSWORD_FIELD = Locator(LocatorStrategy.ID, "password")
    LOGIN_BUTTON = Locator(LocatorStrategy.CSS, "button[type='submit']")
    ERROR_MESSAGE = Locator(LocatorStrategy.CSS, ".error-message")
    REMEMBER_ME = Locator(LocatorStrategy.ID, "remember-me")

    # For applications without stable IDs, use XPath
    # LOGIN_BUTTON = Locator(LocatorStrategy.XPATH, "//button[contains(text(), 'Login')]")

    # For accessibility-first approach
    # LOGIN_BUTTON = Locator(LocatorStrategy.ROLE, "button[name='Login']")


class LoginPage(BasePageObject):
    """
    Login Page Object.
    
    Encapsulates all login-related interactions.
    Hides implementation details (components, locators) from step definitions.
    
    Usage in steps:
        login_page = LoginPage(page)
        login_page.login("username", "password")
        login_page.verify_error_displayed()
    """

    def __init__(self, page):
        """
        Initialize Login Page.
        
        Args:
            page: Playwright Page object
        """
        super().__init__(page, page_name="LoginPage")

        # Initialize components
        self.username_input = TextInputComponent(
            self, LoginPageLocators.USERNAME_FIELD, "Username Input"
        )
        self.password_input = TextInputComponent(
            self, LoginPageLocators.PASSWORD_FIELD, "Password Input"
        )
        self.login_button = ButtonComponent(
            self, LoginPageLocators.LOGIN_BUTTON, "Login Button"
        )

    def navigate_to_login(self, base_url: Optional[str] = None) -> None:
        """
        Navigate to login page.
        
        Args:
            base_url: Base URL (from config if not provided)
        """
        if base_url is None:
            base_url = self.config.get("base_url", "http://localhost:3000")

        login_url = f"{base_url}/login"
        self.navigate_to(login_url)
        self._logger.info("Navigated to Login page")

    def login(self, username: str, password: str) -> None:
        """
        Perform login with credentials.
        
        Args:
            username: Username
            password: Password
        """
        self._logger.info(f"Logging in with username: {username}")

        # Fill credentials
        self.username_input.fill(username)
        self.password_input.fill(password)

        # Click login button
        self.login_button.click()

        self._logger.info("Login submitted")

    def verify_error_displayed(self, error_text: Optional[str] = None) -> bool:
        """
        Verify error message is displayed.
        
        Args:
            error_text: Expected error text (optional)
            
        Returns:
            True if error is visible
        """
        is_visible = self.is_visible(
            LoginPageLocators.ERROR_MESSAGE.value,
            LoginPageLocators.ERROR_MESSAGE.strategy,
        )

        if is_visible and error_text:
            actual_error = self.get_text(
                LoginPageLocators.ERROR_MESSAGE.value,
                LoginPageLocators.ERROR_MESSAGE.strategy,
            )
            if error_text not in actual_error:
                self._logger.warning(f"Error text mismatch. Expected: {error_text}, Got: {actual_error}")
                return False

        self._logger.info(f"Error message visible: {is_visible}")
        return is_visible

    def get_error_message(self) -> str:
        """
        Get error message text.
        
        Returns:
            Error message
        """
        return self.get_text(
            LoginPageLocators.ERROR_MESSAGE.value,
            LoginPageLocators.ERROR_MESSAGE.strategy,
        )

    def is_login_button_enabled(self) -> bool:
        """Check if login button is enabled."""
        return self.login_button.is_enabled()

    def wait_for_login_button_enabled(self) -> None:
        """Wait for login button to be enabled."""
        self.login_button.wait_for_enabled()
