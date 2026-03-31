# Comprehensive Test Automation Framework

A scalable, extensible automation framework supporting **UI (Playwright)**, **API (requests)**, **Database**, and **AWS** testing. Built with clean code principles (SOLID, DRY, KISS), Page Object Model (POM), and Pytest-BDD.

## Features

✅ **Multi-Type Automation**
- UI automation with Playwright (supports Chrome, Firefox, Safari)
- API automation with requests library
- Database automation (PostgreSQL, MySQL, SQLite)
- AWS automation (S3, Lambda, RDS)
- Hybrid scenarios combining multiple types

✅ **Architecture**
- Layered architecture (UI, API, DB, AWS layers)
- Service layer for business logic orchestration
- Loose coupling between automation types
- Dependency injection via Pytest fixtures
- Page Object Model (POM) + Component Pattern

✅ **Code Quality**
- SOLID principles (Single Responsibility, Open/Closed, etc.)
- DRY (Don't Repeat Yourself) - reusable components and services
- KISS (Keep It Simple, Stupid)
- Clean, readable code with extensive documentation

✅ **Configuration**
- TOML-based configuration with environment support (dev, staging, prod)
- Secrets management (git-ignored)
- Environment variable overrides
- Multi-database support

✅ **Testing**
- Pytest + pytest-BDD for behavior-driven testing
- Parallel test execution with pytest-xdist
- Comprehensive reporting (HTML, JSON, Allure)
- Logging with structured output

✅ **Extensibility**
- Ready for future expansion (AWS, DB layers are stubs)
- Add new pages, endpoints, repositories with minimal code
- Reuse components across applications and automation types

## Project Structure

```
PYTHON-BDD-Automation/
├── src/                          # Source code
│   ├── core/                     # Base classes, exceptions, enums
│   │   ├── base_client.py       # Base client for all layers
│   │   ├── base_page.py         # Base page object for UI
│   │   ├── base_endpoint.py     # Base endpoint for API
│   │   ├── base_repository.py   # Base repository for DB
│   │   ├── context.py           # Test context (shared state)
│   │   ├── config_loader.py     # Configuration management
│   │   ├── enums.py             # Enums for frameworks
│   │   └── exceptions.py        # Custom exceptions
│   ├── layers/                   # Automation layers
│   │   ├── ui/                  # UI layer (Playwright)
│   │   │   ├── locators/        # Element locators
│   │   │   ├── components/      # Reusable UI components
│   │   │   ├── pages/           # Page objects
│   │   │   └── ui_client.py     # Browser manager
│   │   ├── api/                 # API layer (requests)
│   │   │   ├── endpoints/       # API endpoints
│   │   │   ├── clients/         # API clients
│   │   │   └── api_client.py    # Session manager
│   │   ├── database/            # Database layer (SQL)
│   │   │   ├── repositories/    # Data access objects
│   │   │   └── database_client.py
│   │   └── aws/                 # AWS layer (boto3)
│   │       ├── services/        # AWS services
│   │       └── aws_client.py
│   ├── services/                # Business logic orchestration
│   │   └── user_service.py      # Example service
│   ├── fixtures/                # Pytest fixtures (DI)
│   │   └── conftest.py          # Fixture definitions
│   └── utils/                   # Utilities
│       ├── logger.py            # Logging
│       └── retry.py             # Retry logic
├── config/                       # Configuration files
│   ├── config.toml              # Main config (environment-specific)
│   └── secrets.toml.example     # Secrets template (git-ignored)
├── features/                     # BDD test scenarios
│   ├── ui/                      # UI test features
│   │   └── login.feature        # Example login feature
│   ├── api/                     # API test features
│   │   └── users_api.feature    # Example API feature
│   ├── integration/             # Integration test features
│   │   └── user_journey.feature # Example integration
│   └── steps/                   # Step definitions
│       ├── ui_steps.py
│       ├── api_steps.py
│       └── integration_steps.py
├── tests/                       # Unit/integration tests
│   └── conftest.py              # Root pytest configuration
├── reports/                     # Test reports (generated)
├── logs/                        # Test logs (generated)
├── scripts/                     # Helper scripts
├── Makefile                     # Build targets
├── pyproject.toml               # Project config & dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Quick Start

### 1. Install Dependencies

```bash
# Install with PDM
pdm install

# Or with pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Configure Environment

```bash
# Create secrets file (git-ignored)
cp config/secrets.toml.example config/secrets.toml

# Edit config/config.toml and config/secrets.toml with your settings
# Update environment URLs, credentials, etc.
```

### 3. Run Tests

```bash
# Run all tests
make test

# Run UI tests only
make test-ui

# Run API tests only
make test-api

# Run integration tests
make test-integration

# Run all tests in parallel
make test-all

# Run smoke tests
make test-smoke

# Run on specific environment
make test-dev      # dev environment
make test-staging  # staging environment
```

### 4. View Reports

```bash
# Generate reports
make report

# Open Allure report
make report-open
```

## Usage Examples

### UI Automation (Page Object Model)

```python
from src.layers.ui.pages.login_page import LoginPage

# Create page object
login_page = LoginPage(page)

# Use page methods (components are hidden)
login_page.navigate_to_login()
login_page.login("username", "password")
login_page.verify_error_displayed()
```

### API Automation

```python
from src.layers.api.endpoints.example_endpoints import UserEndpoint

endpoint = UserEndpoint(session, base_url)

# Straightforward API calls
users = endpoint.get_all_users()
new_user = endpoint.create_user({"name": "John", "email": "john@example.com"})
updated = endpoint.update_user(1, {"name": "Jane"})
endpoint.delete_user(1)
```

### Service Layer (Combining Multiple Layers)

```python
from src.services.user_service import UserService

service = UserService(test_context)

# Create user via API, verify in DB, test via UI
user = service.create_and_verify_user("john_doe", "john@example.com")
service.login_user_via_api("john_doe", "password")
# ... more operations ...
```

### BDD Scenarios (Gherkin)

```gherkin
Feature: User Management
  Scenario: Create and verify user
    Given the API is accessible
    When I create a new user via API with name "John" and email "john@example.com"
    Then the user should be created with status code 201
    And I can verify the user exists in the database
```

## Architecture Principles

### Loose Coupling
Steps, pages, endpoints are independent. Shared state via `TestContext` (not global). Steps can be combined in any order.

### Model-View Pattern
- **Pages/Endpoints**: Define WHAT elements/operations exist
- **Steps**: Define WHEN/HOW they're used in tests
- **Services**: Define business logic that may combine multiple layers

### Dependency Injection
Fixtures inject clients and context. Per-test isolation for parallel execution.

### Extensibility
- Add new pages: `src/layers/ui/pages/my_page.py`
- Add new endpoints: `src/layers/api/endpoints/my_endpoint.py`
- Add new repositories: `src/layers/database/repositories/my_repo.py`
- Services orchestrate everything

## Configuration

### TOML Configuration (`config/config.toml`)

```toml
[environment.dev]
base_url = "http://localhost:3000"
api_base_url = "http://localhost:8080/api"
headless = false

[environment.dev.database]
host = "localhost"
port = 5432
name = "test_db"
```

### Override with Environment Variables

```bash
export BASE_URL="https://app.example.com"
export ENVIRONMENT="production"
export HEADLESS="true"
pytest features/
```

## Parallel Execution

```bash
# Run tests in parallel (auto-detects CPU count)
pytest features/ -n auto

# Run with specific worker count
pytest features/ -n 4
```

## Debugging

### Enable Debug Logging

```bash
pytest features/ -v --log-cli-level=DEBUG
```

### Take Screenshots on Failure

Screenshots are automatically captured if `screenshot_on_failure` is enabled in config.

### Browser Headless Mode

```bash
# Run with browser UI visible
HEADLESS=false pytest features/ui/
```

## Advanced Features

### Custom Assertions

```python
from src.utils.assertions_helper import assert_lists_equal

assert_lists_equal(api_users, db_users, key="email")
```

### Retry Logic

```python
from src.utils.retry import retry_on_exception

@retry_on_exception(max_attempts=3, delay=2.0)
def flaky_operation():
    return do_something()
```

### Test Data Factory

```python
from src.utils.test_data_factory import UserDataFactory

user_data = UserDataFactory.create_random_user()
user_with_role = UserDataFactory.create_user(role="admin")
```

## Best Practices

1. **One Assertion per Step**: Each step should verify one thing
2. **Reuse Components**: Use `TextInputComponent`, `ButtonComponent` instead of finding elements
3. **Use Services for Workflows**: Combine API + DB + UI via services
4. **Page Objects are Gods**: All elements and their interactions go in pages
5. **Loose Coupling**: Don't depend on previous step results in context.test_data keys
6. **DRY**: Extract common patterns to base classes and utilities
7. **Readable Tests**: Test names should describe the business behavior

## Troubleshooting

### Playwright Not Found
```bash
playwright install
```

### Database Connection Fails
- Check `config/config.toml` database configuration
- Verify database is running
- Check `config/secrets.toml` for credentials

### Tests Run Slowly
- Enable parallel execution: `pytest -n auto`
- Check timeouts in config
- Profile with: `pytest --durations=10`

### Allure Reports Not Generated
```bash
pip install allure-pytest
pytest features/ --alluredir=reports/allure
allure serve reports/allure
```

## Contributing

1. Follow code style: `make format`
2. Run linting: `make lint`
3. Write tests for new features
4. Update dependencies in `pyproject.toml`

## License

MIT

## Support

For issues and feature requests, contact the development team.
