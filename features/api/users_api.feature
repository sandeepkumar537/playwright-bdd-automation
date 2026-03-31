Feature: User Management - API Automation
  Demonstrate API automation using RESTful endpoints

  @api @smoke
  Scenario: Get all users via API
    When I fetch all users from the API
    Then the response should have status code 200
    And the response should be a list of users

  @api
  Scenario: Create new user via API
    Given I have user data with name "Jane Doe" and email "jane@example.com"
    When I create a new user via the API
    Then the user should be created with status code 201
    And the response should contain user ID
    And the created user email should be "jane@example.com"

  @api
  Scenario: Get user by ID
    Given a user exists with ID 1
    When I fetch the user with ID 1 from the API
    Then the response should have status code 200
    And the response should contain user information

  @api
  Scenario: Update user via API
    Given a user exists with ID 1
    And I have updated user data with name "John Updated"
    When I update the user via the API
    Then the response should have status code 200
    And the user name should be "John Updated"

  @api
  Scenario: Delete user via API
    Given a user exists with ID 1
    When I delete the user via the API
    Then the response should have status code 204
    And the user should not exist

  @api
  Scenario: Authentication token is required for API calls
    When I try to fetch all users without authentication
    Then the response should have status code 401
    And the response should contain error message
