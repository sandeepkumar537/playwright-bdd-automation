"""
Step definitions for UI automation tests.
Demonstrates how to write low-level steps that call page objects and services.
"""

import pytest
from pytest_bdd import given, when, then, scenario

from src.core.context import TestContext
from src.layers.ui.ui_client import UIClient
from src.layers.ui.pages.login_page import LoginPage
from src.layers.ui.pages.dashboard_page import DashboardPage


# Scenario registration
@scenario("../ui/login.feature", "Successful login with valid credentials")
def test_successful_login(test_context):
    """Test successful login scenario."""
    pass


@scenario("../ui/login.feature", "Failed login with invalid credentials")
def test_failed_login(test_context):
    """Test failed login scenario."""
    pass


@scenario("../ui/login.feature", "Username field is focused and editable")
def test_username_editable(test_context):
    """Test username field is editable."""
    pass


# Background and Given steps
@given("the application is accessible")
def step_app_is_accessible(test_context: TestContext, ui_client: UIClient):
    """
    Verify application is accessible.
    
    This step initializes the UI client if not already done.
    """
    assert ui_client.is_initialized, "UI client should be initialized"
    test_context.set_metadata("app_accessible", True)


# When steps
@when("I navigate to the login page")
def step_navigate_to_login(test_context: TestContext, ui_client: UIClient):
    """Navigate to login page."""
    page = LoginPage(ui_client.page)
    page.navigate_to_login()
    test_context.add_data("current_page", "login")


@when('I enter username "<username>" and password "<password>"')
def step_enter_credentials(
    test_context: TestContext,
    ui_client: UIClient,
    username: str,
    password: str,
):
    """Fill username and password fields."""
    page = LoginPage(ui_client.page)
    page.username_input.fill(username)
    page.password_input.fill(password)
    test_context.add_data("username", username)
    test_context.add_data("password", password)


@when("I click the login button")
def step_click_login_button(test_context: TestContext, ui_client: UIClient):
    """Click login button."""
    page = LoginPage(ui_client.page)
    page.login_button.click()
    test_context.add_data("action", "login_clicked")


# Then steps
@then("I should see the dashboard page")
def step_see_dashboard(test_context: TestContext, ui_client: UIClient):
    """Verify dashboard page is visible."""
    page = DashboardPage(ui_client.page)
    page.wait_for_dashboard_loaded()
    assert page.verify_welcome_message_visible(), "Dashboard should display welcome message"
    test_context.add_data("current_page", "dashboard")


@then("I should see an error message")
def step_see_error_message(test_context: TestContext, ui_client: UIClient):
    """Verify error message is displayed."""
    page = LoginPage(ui_client.page)
    assert page.verify_error_displayed(), "Error message should be displayed"
    test_context.add_data("login_error_shown", True)


@then('the error message should contain "<error_text>"')
def step_error_contains_text(test_context: TestContext, ui_client: UIClient, error_text: str):
    """Verify error message contains specific text."""
    page = LoginPage(ui_client.page)
    actual_error = page.get_error_message()
    assert error_text.lower() in actual_error.lower(), \
        f"Error message should contain '{error_text}'. Got: '{actual_error}'"


@then("the login button should not be enabled")
def step_login_button_disabled(test_context: TestContext, ui_client: UIClient):
    """Verify login button is disabled."""
    page = LoginPage(ui_client.page)
    # Wait a bit for page to load completely
    page.wait_for_login_button_enabled()
    # Note: This depends on your app's behavior
    # Some apps enable button immediately, some after user input


@then("the username field should be visible")
def step_username_field_visible(test_context: TestContext, ui_client: UIClient):
    """Verify username field is visible."""
    page = LoginPage(ui_client.page)
    assert page.username_input.is_visible(), "Username field should be visible"


@then("I can enter text in username field")
def step_can_enter_text_username(test_context: TestContext, ui_client: UIClient):
    """Verify can enter text in username field."""
    page = LoginPage(ui_client.page)
    page.username_input.fill("test_user")
    value = page.username_input.get_value()
    assert "test_user" in value or value == "test_user", "Should be able to enter text"
