Feature: User Journey - Integration Testing
  Demonstrate combining UI, API, and Database automation in a single scenario

  @integration @smoke
  Scenario: Complete user registration and verification flow
    Given the API is accessible
    And the application is accessible
    When I create a new user via API with name "Test User" and email "test@example.com"
    Then the user should be created with status code 201
    And I can verify the user exists in the database with email "test@example.com"
    When I navigate to the application
    And I log in with the created user credentials
    Then I should see the dashboard page
    And the welcome message should contain "Test User"

  @integration
  Scenario: Multi-step user management workflow
    Given I have a test user "workflow_user"
    When I create the user via API
    And I can fetch the user from the database
    And the API returns the same user data
    Then all three layers (API, DB, and UI browsing) are consistent

  @integration
  Scenario: User list consistency across layers
    Given the API is accessible
    And the database is connected
    When I fetch all users from the API
    And I fetch all users from the database
    Then the user count should match between API and database
