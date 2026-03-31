# Setup and Getting Started Guide

## Prerequisites

- Python 3.10 or higher
- PDM (Python Dependency Manager)
- Git (for version control)
- Modern web browser (Chrome, Firefox, or Safari)

## Initial Setup

### Step 1: Install PDM

```bash
# On macOS with Homebrew
brew install pdm

# On Ubuntu/Debian
pip install pdm

# Or visit: https://pdm.fming.dev/
```

### Step 2: Install Project Dependencies

```bash
# Navigate to project directory
cd PYTHON-BDD-Automation

# Install all dependencies using PDM
pdm install

# This installs:
# - Playwright (UI automation)
# - requests (API automation)
# - pytest & pytest-bdd (testing framework)
# - pytest-xdist (parallel execution)
# - SQLAlchemy (database ORM)
# - boto3 (AWS SDK)
# - And other utilities
```

### Step 3: Install Playwright Browsers

```bash
# Install Chromium, Firefox, and WebKit browsers
pdm run playwright install

# Or directly
playwright install
```

### Step 4: Configure Environment

#### Copy Secrets Template

```bash
# Copy secrets template
cp config/secrets.toml.example config/secrets.toml

# Edit secrets file with actual credentials (DO NOT commit to git)
# config/secrets.toml
```

#### Update Configuration

Edit `config/config.toml`:

```toml
[environment.dev]
base_url = "http://your-app-dev.com"
api_base_url = "http://your-api-dev.com"

[environment.dev.database]
host = "localhost"
port = 5432
name = "dev_db"
user = "test_user"

[environment.dev.aws]
region = "us-east-1"
use_local_stack = false
```

Edit `config/secrets.toml`:

```toml
[environment.dev.database]
password = "your_db_password"

[environment.dev]
api_key = "your_api_key"
auth_token = "your_auth_token"
```

### Step 5: Verify Installation

```bash
# Run a simple test to verify everything works
pytest --version

# Run pytest configuration check
pytest --collect-only features/ui/login.feature

# This should list the test without errors
```

## First Test Run

### Run Example UI Test

```bash
# Navigate to project root
cd PYTHON-BDD-Automation

# Run a single feature
pytest features/ui/login.feature -v

# Run with browser visible
HEADLESS=false pytest features/ui/login.feature -v

# Run with detailed logging
pytest features/ui/login.feature -v -s --log-cli-level=DEBUG
```

### Run Example API Test

```bash
# Run API tests
pytest features/api/users_api.feature -v

# Run with specific marker
pytest -m api -v
```

### Run All Tests

```bash
# Run all tests
pytest features/ -v

# Run in parallel
pytest features/ -v -n auto

# Run specific environment
ENVIRONMENT=staging pytest features/ -v
```

## Common Setup Issues

### Issue: `playwright command not found`

**Solution:** Install Playwright package:
```bash
pip install playwright
playwright install
```

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution:** Ensure you're running pytest from project root:
```bash
cd PYTHON-BDD-Automation
pytest features/
```

### Issue: `ConnectionRefusedError: Cannot connect to application`

**Solution:** Verify application is running on configured URL:
```bash
# Check config/config.toml for correct base_url
# Make sure application is running on that URL
curl http://localhost:3000  # or your configured URL
```

### Issue: `Database connection refused`

**Solution:** Check database is running:
```bash
# PostgreSQL example
psql -h localhost -U test_user -d dev_db

# Or check config/config.toml database settings
```

## IDE Setup

### VS Code

1. Install Python extension
2. Install Pylance for type hints
3. Install Pytest extension (optional)

**.vscode/settings.json example:**
```json
{
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "pytest"
}
```

### PyCharm

1. Mark `src` directory as Sources Root
2. Configure test runner as pytest
3. Set Python interpreter to virtual environment

## Git Setup

```bash
# Initialize git (if not already done)
git init

# Create .gitignore (already included)
# Make sure these are ignored:
# - config/secrets.toml
# - reports/
# - logs/
# - .venv/
# - __pycache__/

# Initial commit
git add .
git commit -m "Initial framework setup"
```

## Environment Variables

You can override config with environment variables:

```bash
# Set environment
export ENVIRONMENT=staging

# Set application URL
export BASE_URL="https://staging.example.com"

# Set API URL
export API_BASE_URL="https://api-staging.example.com"

# Set log level
export LOG_LEVEL=DEBUG

# Set headless mode
export HEADLESS=false

# Run tests with env vars
pytest features/ -v
```

## Running Tests from CLI

```bash
# All tests
make test

# By type
make test-ui          # UI only
make test-api         # API only
make test-integration # Integration only

# By environment
make test-dev         # Dev environment
make test-staging     # Staging environment

# Smoke tests
make test-smoke

# Parallel execution
pytest features/ -n auto

# With specific marker
pytest -m smoke -m ui -v

# Generate reports
make report

# View reports
make report-open
```

## Continuous Integration Setup

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Automation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install pdm
          pdm install
          playwright install
      - name: Run tests
        run: make test-all
      - name: Upload reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: reports
          path: reports/
```

## Troubleshooting

### Debug Mode

Enable detailed logging:
```bash
pytest features/ -v -s --log-cli-level=DEBUG
```

### Take Screenshots

Enable screenshots in config:
```toml
[default]
screenshot_on_failure = true
screenshot_on_success = false
```

Screenshots saved to `screenshots/` directory.

### Check Configuration

```python
# Quick config check script
from src.core.config_loader import ConfigLoader

config = ConfigLoader.get_instance()
print(f"Environment: {config.get('environment')}")
print(f"Base URL: {config.get('base_url')}")
print(f"API URL: {config.get('api_base_url')}")
```

## Next Steps

1. **Customize Configuration**: Update `config/config.toml` for your application
2. **Create App-Specific Pages**: Add pages in `src/layers/ui/pages/`
3. **Create Endpoints**: Add endpoints in `src/layers/api/endpoints/`
4. **Write Scenarios**: Add .feature files in `features/`
5. **Implement Steps**: Add step definitions in `features/steps/`

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for detailed guides on extending the framework.
