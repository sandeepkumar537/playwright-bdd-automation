# Test automation framework build and test targets

.PHONY: help install test test-ui test-api test-integration test-all report clean

help:
	@echo "Test Automation Framework Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install         Install dependencies with PDM"
	@echo "  install-dev     Install dependencies with dev extras"
	@echo "  test            Run all tests"
	@echo "  test-ui         Run UI automation tests"
	@echo "  test-api        Run API automation tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-all        Run all tests with parallel execution"
	@echo "  test-smoke      Run smoke tests only"
	@echo "  test-dev        Run tests on dev environment"
	@echo "  test-staging    Run tests on staging environment"
	@echo "  report          Generate HTML and Allure reports"
	@echo "  report-open     Open Allure report in browser"
	@echo "  clean           Clean up generated files and reports"
	@echo "  lint            Run code linting"
	@echo "  format          Format code with black"
	@echo ""

install:
	pdm install

install-dev:
	pdm install -d

test:
	pytest features/ tests/ -v --tb=short

test-ui:
	pytest features/ui/ -v --tb=short -m ui

test-api:
	pytest features/api/ -v --tb=short -m api

test-integration:
	pytest features/integration/ -v --tb=short -m integration

test-all:
	pytest features/ tests/ -v --tb=short -n auto

test-smoke:
	pytest -m smoke -v --tb=short

test-dev:
	ENVIRONMENT=dev pytest features/ tests/ -v --tb=short

test-staging:
	ENVIRONMENT=staging pytest features/ tests/ -v --tb=short

report:
	pytest features/ tests/ -v --tb=short --html=reports/report.html --self-contained-html --alluredir=reports/allure

report-open:
	allure serve reports/allure

clean:
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf *.egg-info

lint:
	pytest --flake8 features/ src/ tests/

format:
	black features/ src/ tests/ --line-length 100
	isort features/ src/ tests/ --profile black

.PHONY: install install-dev test test-ui test-api test-integration test-all test-smoke test-dev test-staging report report-open clean lint format
