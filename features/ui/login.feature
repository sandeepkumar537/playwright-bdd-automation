Feature: User Login - UI Automation
  Demonstrate UI automation using Page Object Model pattern

  Background:
    Given the application is accessible

  @ui @smoke
  Scenario: Successful login with valid credentials
    When I navigate to the login page
    And I enter username "john_doe" and password "TestPassword123!"
    And I click the login button
    Then I should see the dashboard page

  @ui
  Scenario: Failed login with invalid credentials
    When I navigate to the login page
    And I enter username "invalid_user" and password "wrong_password"
    And I click the login button
    Then I should see an error message
    And the error message should contain "Invalid credentials"

  @ui
  Scenario: Login button is disabled initially
    When I navigate to the login page
    Then the login button should not be enabled

  @ui
  Scenario: Username field is focused and editable
    When I navigate to the login page
    Then the username field should be visible
    And I can enter text in username field
