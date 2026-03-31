"""
Step definitions for integration tests.
Demonstrates combining UI, API, and Database automation in single scenarios.
"""

import pytest
from pytest_bdd import given, when, then, scenario

from src.core.context import TestContext
from src.layers.ui.ui_client import UIClient
from src.layers.api.api_client import APIClient
from src.layers.database.database_client import DatabaseClient
from src.services.user_service import UserService


# Scenario registration
@scenario("../integration/user_journey.feature", "Complete user registration and verification flow")
def test_complete_user_flow():
    """Test complete user registration flow."""
    pass


# Background steps (these can be reused from ui_steps and api_steps)

# Given steps for integration
@given("the application is accessible")
def step_app_accessible(ui_client: UIClient):
    """Application is accessible."""
    assert ui_client.is_initialized


@given("the API is accessible")
def step_api_accessible(api_client: APIClient):
    """API is accessible."""
    assert api_client.is_initialized


@given("the database is connected")
def step_database_connected(db_client: DatabaseClient):
    """Database is connected."""
    assert db_client.is_connected()


@given('I have a test user "<username>"')
def step_have_test_user(test_context: TestContext, username: str):
    """Store test username."""
    test_context.add_data("test_username", username)


# When steps for integration
@when('I create a new user via API with name "<name>" and email "<email>"')
def step_create_user_integration(
    test_context: TestContext,
    user_service: UserService,
    name: str,
    email: str,
):
    """Create user via API using service."""
    password = "TestPassword123!"
    user = user_service.create_user_via_api({
        "name": name,
        "email": email,
        "password": password,
    })
    test_context.add_data("api_user", user)
    test_context.add_data("test_email", email)


@when("I can verify the user exists in the database with email \"<email>\"")
def step_verify_user_in_db(
    test_context: TestContext,
    user_service: UserService,
    email: str,
):
    """Verify user exists in database."""
    from src.layers.database.repositories.user_repository import UserRepository
    
    if test_context.db_client:
        repo = UserRepository(test_context.db_client.connection)
        db_user = repo.get_user_by_email(email)
        assert db_user is not None, f"User {email} should exist in database"
        test_context.add_data("db_user", db_user)


@when("I navigate to the application")
def step_navigate_app(test_context: TestContext, ui_client: UIClient):
    """Navigate to application."""
    from src.layers.ui.pages.login_page import LoginPage
    page = LoginPage(ui_client.page)
    page.navigate_to_login()


@when("I log in with the created user credentials")
def step_login_created_user(
    test_context: TestContext,
    ui_client: UIClient,
):
    """Login with created user."""
    from src.layers.ui.pages.login_page import LoginPage
    
    email = test_context.get_data("test_email")
    password = "TestPassword123!"
    
    page = LoginPage(ui_client.page)
    page.login(email, password)


@when("I create the user via API")
def step_create_user_service(
    test_context: TestContext,
    user_service: UserService,
):
    """Create user via API using service."""
    username = test_context.get_data("test_username")
    user_data = {
        "name": username,
        "email": f"{username}@example.com",
        "password": "TestPassword123!",
    }
    user = user_service.create_user_via_api(user_data)
    test_context.add_data("api_user", user)


@when("I can fetch the user from the database")
def step_fetch_user_db(
    test_context: TestContext,
    db_client: DatabaseClient,
):
    """Fetch user from database."""
    from src.layers.database.repositories.user_repository import UserRepository
    
    if db_client.is_connected():
        repo = UserRepository(db_client.connection)
        api_user = test_context.get_data("api_user")
        db_user = repo.get_user_by_email(api_user.get("email"))
        assert db_user is not None, "User should exist in database"
        test_context.add_data("db_user", db_user)


@when("the API returns the same user data")
def step_api_returns_same_data(
    test_context: TestContext,
    api_client: APIClient,
):
    """Fetch user from API and verify data matches."""
    from src.layers.api.endpoints.example_endpoints import UserEndpoint
    
    api_user = test_context.get_data("api_user")
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    fetched_user = endpoint.get_user(api_user["id"])
    assert fetched_user is not None, "API should return user"
    test_context.add_data("api_user_fetched", fetched_user)


@when("I fetch all users from the API")
def step_fetch_all_users_api(
    test_context: TestContext,
    api_client: APIClient,
):
    """Fetch all users from API."""
    from src.layers.api.endpoints.example_endpoints import UserEndpoint
    
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    users = endpoint.get_all_users()
    test_context.add_data("api_users", users)


@when("I fetch all users from the database")
def step_fetch_all_users_db(
    test_context: TestContext,
    db_client: DatabaseClient,
):
    """Fetch all users from database."""
    from src.layers.database.repositories.user_repository import UserRepository
    
    if db_client.is_connected():
        repo = UserRepository(db_client.connection)
        users = repo.get_all_users()
        test_context.add_data("db_users", users)


# Then steps for integration
@then("the user should be created with status code 201")
def step_user_created_status(test_context: TestContext):
    """Verify user was created."""
    api_user = test_context.get_data("api_user")
    assert api_user is not None, "User should be created"


@then("I should see the dashboard page")
def step_see_dashboard_integration(test_context: TestContext, ui_client: UIClient):
    """Verify dashboard is visible."""
    from src.layers.ui.pages.dashboard_page import DashboardPage
    
    page = DashboardPage(ui_client.page)
    page.wait_for_dashboard_loaded()
    assert page.verify_welcome_message_visible()


@then('the welcome message should contain "<text>"')
def step_welcome_contains_text(
    test_context: TestContext,
    ui_client: UIClient,
    text: str,
):
    """Verify welcome message contains text."""
    from src.layers.ui.pages.dashboard_page import DashboardPage
    
    page = DashboardPage(ui_client.page)
    assert page.verify_welcome_message_visible(text)


@then("all three layers (API, DB, and UI browsing) are consistent")
def step_layers_consistent(test_context: TestContext):
    """Verify data is consistent across layers."""
    api_user = test_context.get_data("api_user_fetched")
    db_user = test_context.get_data("db_user")
    
    if api_user and db_user:
        # Compare key fields
        assert api_user.get("email") == db_user.get("email"), \
            "Email should match between API and DB"


@then("the user count should match between API and database")
def step_user_count_match(test_context: TestContext):
    """Verify user count matches between API and database."""
    api_users = test_context.get_data("api_users", [])
    db_users = test_context.get_data("db_users", [])
    
    api_count = len(api_users) if isinstance(api_users, list) else 0
    db_count = len(db_users) if isinstance(db_users, list) else 0
    
    assert api_count == db_count, \
        f"User count should match. API: {api_count}, DB: {db_count}"
