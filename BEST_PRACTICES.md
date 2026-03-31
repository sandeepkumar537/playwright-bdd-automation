# Best Practices & Patterns

This guide outlines best practices for using and extending the automation framework.

## Code Organization

### File Structure Principles

1. **Keep files focused**: Each file should have a single responsibility
2. **Consistent naming**: Use descriptive names (YourPageLocators, YourEndpoint, YourRepository)
3. **Group related files**: Locators with their pages, endpoints in logical groups
4. **Use init files**: Every package should have `__init__.py` for proper imports

### Example Structure for New Feature

```
src/layers/ui/pages/
├── __init__.py
├── checkout_page_locators.py    # Locators only
├── checkout_page.py             # Page object
├── payment_page_locators.py
└── payment_page.py

features/checkout/
├── checkout.feature
└── payment.feature

features/steps/
└── checkout_steps.py            # Steps for checkout feature
```

## Writing Maintainable Pages

### ✅ Good Page Design

```python
class CheckoutPage(BasePageObject):
    """Checkout page with clear business methods."""
    
    def __init__(self, page):
        super().__init__(page, page_name="CheckoutPage")
        self.product_list = TableComponent(page, CheckoutPageLocators.PRODUCTS)
        self.proceed_button = ButtonComponent(page, CheckoutPageLocators.PROCEED)
    
    def add_product(self, product_name: str) -> None:
        """Add product to cart - business-level method."""
        product_row = self.product_list.find_row(product_name)
        add_btn = product_row.find_element(CheckoutPageLocators.ADD_BUTTON)
        add_btn.click()
    
    def verify_cart_total(self, expected_total: float) -> None:
        """Verify cartotal matches expected."""
        total_element = self.find_element(CheckoutPageLocators.TOTAL_PRICE)
        actual_total = float(total_element.text_content())
        assert actual_total == expected_total
```

### ❌ Bad Page Design

```python
class CheckoutPage(BasePageObject):
    """Poorly designed - too low-level."""
    
    def click_element_by_xpath(self, xpath):
        element = self.page.locator(xpath)
        element.click()
    
    def get_text_from_css(self, css):
        return self.page.locator(css).text_content()
    
    # Steps would call these directly - breaks encapsulation
```

## Writing Effective Steps

### ✅ Good Steps

```python
@when("I add <quantity> <product> items to cart")
@pytest.mark.parametrize("product,quantity", [
    ("Laptop", 1),
    ("Mouse", 2),
    ("Keyboard", 1),
])
def step_add_to_cart(ui_client, test_context, product, quantity):
    page = CheckoutPage(ui_client.page)
    for _ in range(quantity):
        page.add_product(product)
    
    test_context.add_data("products_added", product)
    test_context.add_data("quantity", quantity)
```

### ❌ Bad Steps

```python
@when("I do something")
def step_do_something(ui_client):
    # Too vague - what is "something"?
    ui_client.page.click("//button[1]")
    ui_client.page.fill("//input[@id='search']", "test")
    # No context, no assertion
```

## Using TestContext Effectively

### Adding Data Pattern

```python
@given("I login as <username>")
def step_login(api_client, test_context, username):
    endpoint = AuthEndpoint(api_client.session, api_client.base_url)
    response = endpoint.login(username, "password")
    
    # Store for later use in same test
    test_context.add_data("user_id", response["user_id"])
    test_context.add_data("auth_token", response["token"])
    test_context.add_data("username", username)
```

### Retrieving Data Pattern

```python
@then("I verify user details match API")
def step_verify_user(api_client, test_context):
    user_id = test_context.get_data("user_id")
    username = test_context.get_data("username")
    
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    user = endpoint.get_user(user_id)
    
    assert user["name"] == username
```

### Metadata Pattern

```python
@when("I perform critical action")
def step_critical_action(ui_client, test_context):
    page = YourPage(ui_client.page)
    page.perform_critical_action()
    
    # Mark test metadata
    test_context.set_metadata("critical_action_performed", True)
    test_context.set_metadata("action_time", datetime.now())

@then("I verify action was performed")
def step_verify(test_context):
    assert test_context.get_metadata("critical_action_performed")
```

## Composition Over Inheritance

### ✅ Good Composition

```python
class ComplexWorkflowPage(BasePageObject):
    """Reuse components instead of duplicating code."""
    
    def __init__(self, page):
        super().__init__(page, page_name="ComplexWorkflow")
        # Compose multiple components
        self.form = FormComponent(page, FormLocators.MAIN_FORM)
        self.user_selector = DropdownComponent(page, FormLocators.USER_SELECT)
        self.date_picker = DatePickerComponent(page, FormLocators.DATE)
```

### ❌ Bad Inheritance

```python
class FormPage(BasePageObject):
    def fill_form(self): pass

class UserFormPage(FormPage):
    def select_user(self): pass

class DateFormPage(UserFormPage):
    def select_date(self): pass

# Don't use multiple inheritance chains for UI
```

## Exception Handling

### ✅ Good Exception Handling

```python
from src.core.exceptions import UILayerException, ElementNotFoundError

def fill_optional_field(self, locator: Locator, value: str) -> bool:
    """Fill optional field, return success status."""
    try:
        element = self.find_element(locator)
        element.fill(value)
        return True
    except ElementNotFoundError:
        self._logger.warning(f"Optional field not found: {locator}")
        return False

def click_required_button(self, locator: Locator) -> None:
    """Click required button, raise if not found."""
    try:
        element = self.find_element(locator)
        element.click()
    except ElementNotFoundError as e:
        raise UILayerException(
            f"Required button not found: {locator}"
        ) from e
```

### ❌ Bad Exception Handling

```python
def fill_field(self, locator, value):
    try:
        element = self.page.locator(locator).fill(value)
    except Exception:
        pass  # Silent failures are dangerous!

def click_button(self, locator):
    element = self.page.locator(locator)
    # No exception handling - test crashes without info
    element.click()
```

## Logging Best Practices

### ✅ Good Logging

```python
def login(self, username: str, password: str) -> Dict[str, Any]:
    """Login user."""
    self._logger.info(f"Attempting login for user: {username}")
    
    try:
        response = self.api_client.post(
            "/auth/login",
            json_data={"username": username, "password": password}
        )
        self._logger.debug(f"Login response status: {response.status_code}")
        return response.json()
    except APILayerException as e:
        self._logger.error(f"Login failed for {username}: {str(e)}")
        raise
```

### ❌ Bad Logging

```python
def login(self, username, password):
    response = self.api_client.post("/auth/login", {})
    # No logging means no visibility into test execution
    return response.json()
```

## Configuration Management

### ✅ Good Config Usage

```python
from src.core.config_loader import ConfigLoader

class UIClient(BaseClient):
    def __init__(self, logger, config):
        super().__init__("UIClient", logger, config)
        
        # Read from config with defaults
        self.headless = config.get("headless", True)
        self.timeout = config.get("implicit_wait_seconds", 10)
        self.slow_mo = config.get("slow_motion_ms", 0)
        
        self._logger.info(f"UI Client initialized. Headless: {self.headless}")
```

### ❌ Bad Config Usage

```python
class UIClient:
    def __init__(self):
        # Hard-coded values - can't change per environment
        self.headless = True
        self.timeout = 10
        # No flexibility!
```

## Parallel Execution

### ✅ Safe for Parallel Execution

```python
# Function-scoped fixtures ensure each test gets fresh instance
@pytest.fixture(scope="function")
def ui_client():
    client = UIClient()
    yield client
    client.close()

# Sessions/contexts per-test
@pytest.fixture(scope="function")
def api_client(config_loader):
    session = requests.Session()
    return APIClient(session, config_loader)

# TestContext per-test
@pytest.fixture(scope="function")
def test_context():
    context = TestContext()
    yield context
    # Cleanup
    context.clear()
```

### ❌ Not Safe for Parallel Execution

```python
# Session-scoped = one session for all tests (race conditions!)
@pytest.fixture(scope="session")
def ui_client():
    client = UIClient()
    yield client

# Global state (race conditions!)
GLOBAL_CONTEXT = {}

def test_something():
    GLOBAL_CONTEXT["user_id"] = 123  # Race condition!
```

## API Response Handling

### ✅ Good Response Handling

```python
def create_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
    """Create user and return user ID."""
    response = self.post(
        "/users",
        json_data=user_data,
        expected_status=201  # Validate status code
    )
    
    response_data = self.parse_json_response(response)
    
    # Validate required fields exist
    required_fields = ["id", "email", "username"]
    for field in required_fields:
        if field not in response_data:
            raise APILayerException(f"Missing field in response: {field}")
    
    return response_data
```

### ❌ Bad Response Handling

```python
def create_user(self, user_data):
    response = requests.post(f"{self.base_url}/users", json=user_data)
    # No status code check
    # No error handling
    # Direct parse without validation
    return response.json()
```

## Data-Driven Testing

### ✅ Good Data-Driven Tests

```python
@pytest.mark.parametrize("invalid_email", [
    "notanemail",
    "@example.com",
    "user@",
    "user name@example.com",
    None,
])
def test_invalid_emails(api_client, invalid_email):
    """Test email validation."""
    endpoint = UserEndpoint(api_client.session, api_client.base_url)
    
    with pytest.raises(APILayerException):
        endpoint.create_user({
            "email": invalid_email,
            "username": "testuser",
            "password": "Test@123"
        })
```

### Feature File with Examples

```gherkin
Scenario Outline: Create user with different roles
  When I create a user with role "<role>"
  Then user should have "<role>" permissions

  Examples:
    | role  |
    | admin |
    | user  |
    | guest |
```

## Retry and Wait Strategies

### ✅ Good Retry Usage

```python
from src.utils.retry import RetryConfig, retry_with_backoff

@retry_with_backoff(
    max_attempts=3,
    initial_delay=1,
    backoff_factor=2
)
def submit_form_with_retry(self) -> None:
    """Submit form with automatic retry on failure."""
    element = self.find_element(self.SUBMIT_BUTTON)
    element.click()
    self._logger.info("Form submitted successfully")

# Or in steps
@then("I verify element appears")
def step_wait_for_element(ui_client):
    page = YourPage(ui_client.page)
    page.wait_for_element(YourPageLocators.SUCCESS_MESSAGE)
```

### ❌ Bad Retry Usage

```python
# Hard-coded waits (slow, unreliable)
def submit_form(self):
    element = self.page.locator(xpath)
    element.click()
    time.sleep(5)  # Fixed wait is bad!

# No retry logic (flaky tests)
def verify_text(self):
    assert self.page.locator(xpath).text_content() == "Expected"
```

## Documentation

### ✅ Good Docstrings

```python
def create_user_via_api(
    self,
    email: str,
    username: str,
    password: str
) -> Dict[str, Any]:
    """
    Create user account via API.
    
    Args:
        email: User email address (must be unique)
        username: Display username (3-50 characters)
        password: User password (min 8 chars, must have special char)
    
    Returns:
        dict: Created user data with id, email, username, created_at
    
    Raises:
        APILayerException: If email already exists or validation fails
        
    Example:
        >>> user = endpoint.create_user_via_api(
        ...     "user@example.com",
        ...     "testuser",
        ...     "Test@123"
        ... )
        >>> assert user["email"] == "user@example.com"
    """
```

### Feature File Documentation

```gherkin
Feature: User Management
  As a system administrator
  I want to manage user accounts
  So that I can control access to the system

  Scenario: Create new user with valid credentials
    Given I am logged in as administrator
    When I create a user with email "new@example.com"
    Then user should be created successfully
    And user should have default role "user"
```

## Performance Tips

1. **Reuse browser context**: Don't create new browser for each test
2. **Use fixture scoping wisely**: Session scope for expensive setup
3. **Parallel execution**: Use `pytest-xdist` for CI/CD pipelines
4. **Mock external APIs**: Don't test third-party services
5. **Efficient waits**: Use smart waits, not fixed sleeps

## Common Pitfalls to Avoid

1. ❌ Hard-coding test data in code (use config or fixtures)
2. ❌ Tight coupling between steps (use TestContext for sharing)
3. ❌ Long running tests (break into smaller scenarios)
4. ❌ Global state (use fixtures with proper scope)
5. ❌ No error context (log before assertions fail)
6. ❌ Ignoring timeouts (always set explicit waits)
7. ❌ Brittle selectors (use stable locators, document why)

---

See [CUSTOMIZATION.md](CUSTOMIZATION.md) and [SETUP.md](SETUP.md) for more guides.
