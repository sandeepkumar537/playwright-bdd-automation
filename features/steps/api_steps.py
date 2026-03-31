"""
Step definitions for API automation tests.
Demonstrates how to write API-focused steps that call endpoints and services.
"""

import pytest
from pytest_bdd import given, when, then, scenario

from src.core.context import TestContext
from src.layers.api.api_client import APIClient
from src.layers.api.endpoints.example_endpoints import UserEndpoint, AuthEndpoint


# Scenario registration
@scenario("../api/users_api.feature", "Get all users via API")
def test_get_all_users():
    """Test get all users scenario."""
    pass


@scenario("../api/users_api.feature", "Create new user via API")
def test_create_user():
    """Test create user scenario."""
    pass


# Given steps
@given("the API is accessible")
def step_api_accessible(api_client: APIClient):
    """Verify API is accessible."""
    assert api_client.is_initialized, "API client should be initialized"


@given('I have user data with name "<name>" and email "<email>"')
def step_have_user_data(test_context: TestContext, name: str, email: str):
    """Prepare user data."""
    user_data = {
        "name": name,
        "email": email,
        "password": "TestPassword123!",
    }
    test_context.add_data("user_data", user_data)


@given("a user exists with ID 1")
def step_user_exists_id_1(test_context: TestContext, api_client: APIClient):
    """Assume a user with ID 1 exists."""
    test_context.add_data("user_id", 1)


@given('I have updated user data with name "<name>"')
def step_have_updated_user_data(test_context: TestContext, name: str):
    """Prepare updated user data."""
    updated_data = {
        "name": name,
    }
    test_context.add_data("updated_user_data", updated_data)


# When steps
@when("I fetch all users from the API")
def step_fetch_all_users(test_context: TestContext, api_client: APIClient):
    """Fetch all users from API."""
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        users = endpoint.get_all_users()
        test_context.add_data("api_response", users)
        test_context.add_data("response_status", 200)
    except Exception as e:
        test_context.add_data("api_error", str(e))


@when("I create a new user via the API")
def step_create_user_api(test_context: TestContext, api_client: APIClient):
    """Create new user via API."""
    user_data = test_context.get_data("user_data")
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        created_user = endpoint.create_user(user_data)
        test_context.add_data("created_user", created_user)
        test_context.add_data("response_status", 201)
    except Exception as e:
        test_context.add_data("api_error", str(e))


@when("I fetch the user with ID <user_id> from the API")
def step_fetch_user_by_id(test_context: TestContext, api_client: APIClient, user_id: int):
    """Fetch user by ID from API."""
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        user = endpoint.get_user(user_id)
        test_context.add_data("fetched_user", user)
        test_context.add_data("response_status", 200)
    except Exception as e:
        test_context.add_data("api_error", str(e))


@when("I update the user via the API")
def step_update_user_api(test_context: TestContext, api_client: APIClient):
    """Update user via API."""
    user_id = test_context.get_data("user_id")
    updated_data = test_context.get_data("updated_user_data")
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        updated_user = endpoint.update_user(user_id, updated_data)
        test_context.add_data("updated_user_response", updated_user)
        test_context.add_data("response_status", 200)
    except Exception as e:
        test_context.add_data("api_error", str(e))


@when("I delete the user via the API")
def step_delete_user_api(test_context: TestContext, api_client: APIClient):
    """Delete user via API."""
    user_id = test_context.get_data("user_id")
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        endpoint.delete_user(user_id)
        test_context.add_data("response_status", 204)
    except Exception as e:
        test_context.add_data("api_error", str(e))


@when("I try to fetch all users without authentication")
def step_fetch_without_auth(test_context: TestContext, api_client: APIClient):
    """Fetch all users without authentication."""
    # Create a new session without auth token
    import requests
    session = requests.Session()
    endpoint = UserEndpoint(session, api_client.base_url)
    
    try:
        users = endpoint.get_all_users()
    except Exception as e:
        test_context.add_data("api_error", str(e))


# Then steps
@then("the response should have status code <status_code>")
def step_response_status(test_context: TestContext, status_code: int):
    """Verify response status code."""
    current_status = test_context.get_data("response_status")
    assert current_status == status_code, \
        f"Expected status {status_code}, got {current_status}"


@then("the response should be a list of users")
def step_response_is_list(test_context: TestContext):
    """Verify response is a list."""
    response = test_context.get_data("api_response")
    assert isinstance(response, list), "Response should be a list"


@then("the user should be created with status code 201")
def step_user_created(test_context: TestContext):
    """Verify user was created successfully."""
    created_user = test_context.get_data("created_user")
    assert created_user is not None, "User should be created"
    assert "id" in created_user, "Created user should have ID"


@then("the response should contain user ID")
def step_response_contains_id(test_context: TestContext):
    """Verify response contains user ID."""
    created_user = test_context.get_data("created_user")
    assert "id" in created_user, "Response should contain user ID"
    test_context.add_data("created_user_id", created_user["id"])


@then('the created user email should be "<email>"')
def step_verify_user_email(test_context: TestContext, email: str):
    """Verify created user email."""
    created_user = test_context.get_data("created_user")
    assert created_user.get("email") == email, \
        f"User email should be {email}, got {created_user.get('email')}"


@then("the response should contain user information")
def step_response_has_user_info(test_context: TestContext):
    """Verify response contains user information."""
    fetched_user = test_context.get_data("fetched_user")
    assert fetched_user is not None, "Should fetch user"
    assert "id" in fetched_user, "User should have ID"
    assert "name" in fetched_user or "email" in fetched_user, "User should have name or email"


@then('the user name should be "<name>"')
def step_verify_updated_name(test_context: TestContext, name: str):
    """Verify user name was updated."""
    updated_user = test_context.get_data("updated_user_response")
    assert updated_user.get("name") == name, \
        f"User name should be {name}, got {updated_user.get('name')}"


@then("the user should not exist")
def step_user_not_exist(test_context: TestContext, api_client: APIClient):
    """Verify user was deleted."""
    user_id = test_context.get_data("user_id")
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    try:
        endpoint.get_user(user_id)
        assert False, "User should not exist after deletion"
    except Exception:
        # Expected - user not found
        pass


@then("the response should contain error message")
def step_response_has_error(test_context: TestContext):
    """Verify response contains error message."""
    error = test_context.get_data("api_error")
    assert error is not None, "Should have error message"
