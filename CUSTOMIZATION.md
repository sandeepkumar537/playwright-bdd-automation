# Customization Guide - Extending the Framework

This guide explains how to extend the framework for your specific application and automation needs.

## Adding a New Page Object

### Step 1: Define Locators

Create `src/layers/ui/pages/your_page_locators.py`:

```python
from src.layers.ui.locators.base_locator import Locator, BaseLocators
from src.core.enums import LocatorStrategy

class YourPageLocators(BaseLocators):
    """Locators for Your Page."""
    
    # Simple ID locator
    USERNAME = Locator(LocatorStrategy.ID, "username")
    
    # XPath for complex selection (useful for IBM BAW)
    SUBMIT_BUTTON = Locator(LocatorStrategy.XPATH, "//button[@data-test='submit']")
    
    # CSS selector
    SUCCESS_MESSAGE = Locator(LocatorStrategy.CSS, ".success-banner")
    
    # Accessibility-based (recommended)
    LOGIN_BUTTON = Locator(LocatorStrategy.ROLE, "button[name='Login']")
```

### Step 2: Create Page Object

Create `src/layers/ui/pages/your_page.py`:

```python
from src.core.base_page import BasePageObject
from src.layers.ui.components.ui_components import (
    TextInputComponent,
    ButtonComponent,
)
from src.layers.ui.pages.your_page_locators import YourPageLocators

class YourPage(BasePageObject):
    """Your Page Object."""
    
    def __init__(self, page):
        super().__init__(page, page_name="YourPage")
        
        # Initialize components
        self.username = TextInputComponent(
            self, 
            YourPageLocators.USERNAME,
            "Username Field"
        )
        self.submit_button = ButtonComponent(
            self,
            YourPageLocators.SUBMIT_BUTTON,
            "Submit Button"
        )
    
    def perform_action(self, username: str) -> None:
        """Perform business action."""
        self.username.fill(username)
        self.submit_button.click()
        self._logger.info("Action performed")
```

### Step 3: Use in Steps

```python
from pytest_bdd import when
from src.layers.ui.pages.your_page import YourPage

@when('I perform action with username "<username>"')
def step_perform_action(ui_client, username):
    page = YourPage(ui_client.page)
    page.perform_action(username)
```

## Adding a New Component

Custom components for complex UI patterns:

```python
from src.layers.ui.components.ui_components import BaseComponent
from src.layers.ui.locators.base_locator import Locator
from src.core.enums import LocatorStrategy

class DatePickerComponent(BaseComponent):
    """Date picker component."""
    
    def __init__(self, page, locator, component_name="Date Picker"):
        super().__init__(page, locator, component_name)
    
    def select_date(self, date_string: str) -> None:
        """Select date in format YYYY-MM-DD."""
        element = self.find()
        element.fill(date_string)
        self._logger.debug(f"Selected date: {date_string}")
    
    def get_date(self) -> str:
        """Get selected date."""
        element = self.find()
        return element.input_value()
```

## Adding a New API Endpoint

### Step 1: Create Endpoint Class

Create `src/layers/api/endpoints/your_endpoint.py`:

```python
from typing import Dict, Any, Optional
from requests import Session

from src.core.base_endpoint import BaseEndpoint
from src.core.enums import HTTPMethod

class YourEndpoint(BaseEndpoint):
    """Your API Endpoint."""
    
    def __init__(self, session: Session, base_url: str):
        super().__init__(session, base_url, endpoint_name="YourEndpoint")
    
    def get_resource(self, resource_id: int) -> Dict[str, Any]:
        """Get resource by ID."""
        response = self.get(f"/resources/{resource_id}", expected_status=200)
        return self.parse_json_response(response)
    
    def create_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new resource."""
        response = self.post(
            "/resources",
            json_data=resource_data,
            expected_status=201
        )
        return self.parse_json_response(response)
    
    def bulk_update(self, updates: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update resources."""
        response = self.request(
            HTTPMethod.PATCH,
            "/resources/bulk",
            json_data={"updates": updates},
            expected_status=200
        )
        return self.parse_json_response(response)
```

### Step 2: Use in Steps

```python
from pytest_bdd import when
from src.layers.api.endpoints.your_endpoint import YourEndpoint

@when("I create a resource via API")
def step_create_resource(api_client, test_context):
    endpoint = YourEndpoint(api_client.session, api_client.base_url)
    resource = endpoint.create_resource({"name": "Test Resource"})
    test_context.add_data("resource_id", resource["id"])
```

## Adding a New Database Repository

### Step 1: Create Repository

Create `src/layers/database/repositories/your_repository.py`:

```python
from typing import Dict, Any, Optional, List
from src.core.base_repository import BaseRepository

class YourRepository(BaseRepository):
    """Your Data Repository."""
    
    def __init__(self, connection):
        super().__init__(connection, repository_name="YourRepository")
    
    def get_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        query = "SELECT id, name, status FROM your_table WHERE id = %s"
        result = self.execute_query(query, (item_id,), fetch_one=True)
        return dict(result) if result else None
    
    def create(self, item_data: Dict[str, Any]) -> Optional[int]:
        """Create new item."""
        query = """
            INSERT INTO your_table (name, status)
            VALUES (%s, %s)
            RETURNING id
        """
        result = self.execute_query(
            query,
            (item_data.get("name"), item_data.get("status")),
            fetch_one=True
        )
        return result[0] if result else None
    
    def search(self, query_text: str) -> List[Dict[str, Any]]:
        """Search items."""
        query = "SELECT id, name, status FROM your_table WHERE name ILIKE %s"
        results = self.execute_query(query, (f"%{query_text}%",))
        return [dict(row) for row in results] if results else []
```

## Adding a New Service

### Step 1: Create Service Class

Create `src/services/your_service.py`:

```python
from src.core.context import TestContext
from src.utils.logger import Logger

class YourService:
    """Business logic orchestration for Your operations."""
    
    def __init__(self, context: TestContext):
        self.context = context
        self._logger = Logger.get_logger(__name__)
    
    def complex_workflow(self, name: str) -> Dict[str, Any]:
        """Complex workflow combining multiple layers."""
        
        # Step 1: Create via API
        api_result = self._create_via_api(name)
        
        # Step 2: Verify in database
        if self.context.db_client:
            db_result = self._verify_in_db(api_result["id"])
            
        # Step 3: Verify via UI browsing
        if self.context.ui_client:
            self._verify_in_ui(name)
        
        return api_result
    
    def _create_via_api(self, name: str) -> Dict[str, Any]:
        from src.layers.api.endpoints.your_endpoint import YourEndpoint
        
        endpoint = YourEndpoint(
            self.context.api_client.session,
            self.context.api_client.base_url
        )
        return endpoint.create_resource({"name": name})
    
    def _verify_in_db(self, resource_id: int) -> Dict[str, Any]:
        from src.layers.database.repositories.your_repository import YourRepository
        
        repo = YourRepository(self.context.db_client.connection)
        return repo.get_by_id(resource_id)
    
    def _verify_in_ui(self, name: str) -> None:
        # Implement UI verification
        self._logger.info(f"Verified {name} in UI")
```

## Writing BDD Scenarios

### Feature File

Create `features/your_feature/your_scenario.feature`:

```gherkin
Feature: Your Feature
  Description of what you're testing

  @your_tag @smoke
  Scenario: Your scenario description
    Given some precondition
    When I perform an action
    Then I should see expected result
```

### Step Definitions

Add to `features/steps/your_steps.py`:

```python
from pytest_bdd import given, when, then, scenario
from src.core.context import TestContext

@scenario("../your_feature/your_scenario.feature", "Your scenario description")
def test_your_scenario():
    """Test your scenario."""
    pass

@given("some precondition")
def step_precondition(test_context):
    test_context.add_data("precondition", True)

@when("I perform an action")
def step_action(test_context):
    test_context.set_metadata("action_performed", True)

@then("I should see expected result")
def step_verify_result(test_context):
    assert test_context.get_metadata("action_performed")
```

## Configuration for Your App

Edit `config/config.toml`:

```toml
[environment.dev]
base_url = "http://your-app-dev.local:3000"
api_base_url = "http://api-dev.local:8080"
implicit_wait_seconds = 10
headless = false

[environment.dev.database]
host = "localhost"
port = 5432
name = "your_app_db"
user = "app_user"
driver = "postgresql"
```

Edit `config/secrets.toml`:

```toml
[environment.dev.database]
password = "secret_password"

[environment.dev]
api_key = "your_api_key_here"
auth_token = "your_auth_token_here"
```

## Multi-App Support

If testing multiple applications:

### Option 1: Environment Variables

```bash
export APP_TYPE=IBM_BAW
pytest features/
```

Then in pages:
```python
import os
app_type = os.getenv("APP_TYPE", "default")

if app_type == "IBM_BAW":
    # Use BAW-specific locators
    BUTTON = Locator(LocatorStrategy.XPATH, "//ibm:button")
else:
    # Use standard locators
    BUTTON = Locator(LocatorStrategy.CSS, ".button")
```

### Option 2: Separate Feature Sets

```
features/
├── apps/
│   ├── react-app/
│   │   ├── login.feature
│   │   └── dashboard.feature
│   ├── angular-app/
│   │   ├── login.feature
│   │   └── workflow.feature
│   └── baw-app/
│       ├── login.feature
│       └── workflow.feature
```

Run by app:
```bash
pytest features/apps/react-app/ -v
pytest features/apps/baw-app/ -v
```

## Tips for Scaling

1. **Reuse Components**: Extract common patterns into components
2. **Use Services**: Don't duplicate API/DB calls in steps
3. **Base Locators**: Create base locator sets for common elements
4. **Page Inheritance**: Extend common pages for variations
5. **Parameterization**: Use pytest parametrization for data-driven tests

## Performance Optimization

1. **Parallel Execution**: `pytest -n auto`
2. **Fixture Scoping**: Use appropriate fixture scopes
3. **Browser Caching**: Reuse browser contexts when possible
4. **Database Transactions**: Use transactions for faster cleanup
5. **Mock External APIs**: Mock slow external API calls

See [README.md](README.md) for general framework documentation.
