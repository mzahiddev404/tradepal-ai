# Testing Guide - TradePal AI

Complete guide for running and writing tests for the TradePal AI application.

## Overview

The test suite covers API endpoints, agent functionality, and integration scenarios. Tests are organized by functionality and can be run individually or as a complete suite.

## Test Structure

### Backend Tests

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_api_chat.py     # Chat API tests
│   ├── test_api_stock.py    # Stock API tests
│   ├── test_api_upload.py   # Upload API tests
│   └── test_agents.py       # Agent tests
├── pytest.ini               # Pytest configuration
├── requirements-test.txt    # Test dependencies
└── run_tests.py            # Test runner script
```

## Running Tests

### Install Test Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Using the test runner script
python run_tests.py

# Or directly with pytest
pytest tests/ -v

# Or with coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Run Specific Test Files

```bash
# Run only chat API tests
pytest tests/test_api_chat.py -v

# Run only stock API tests
pytest tests/test_api_stock.py -v

# Run only agent tests
pytest tests/test_agents.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest tests/test_api_chat.py::TestChatAPI -v

# Run specific test function
pytest tests/test_api_chat.py::TestChatAPI::test_health_endpoint -v
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Fast execution
- No external dependencies

### Integration Tests
- Test API endpoints
- Test agent interactions
- May require external services

### End-to-End Tests
- Test complete user flows
- Require full application stack
- Slower execution

## Writing Tests

### Example: API Endpoint Test

```python
def test_chat_endpoint_success(client, sample_chat_request):
    """Test successful chat request."""
    response = client.post("/api/chat", json=sample_chat_request)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["status"] == "success"
```

### Example: Agent Test

```python
def test_orchestrator_routing():
    """Test orchestrator routing logic."""
    from utils.orchestrator import OrchestratorAgent
    orchestrator = OrchestratorAgent()
    
    result = orchestrator.route_query("What are your pricing plans?")
    assert result in ["BILLING_AGENT", "GENERAL_AGENT"]
```

## Test Fixtures

### Available Fixtures

- `client`: FastAPI test client
- `sample_chat_request`: Sample chat request data
- `sample_stock_symbol`: Sample stock symbol (TSLA)
- `mock_env_vars`: Mocked environment variables

## Test Coverage

### Current Coverage

- ✅ API endpoint tests
- ✅ Agent initialization tests
- ✅ Basic routing tests
- ⚠️  Full integration tests (requires API keys)
- ⚠️  E2E tests (requires full stack)

### Coverage Goals

- [ ] 80%+ code coverage
- [ ] All API endpoints tested
- [ ] All agents tested
- [ ] Error cases covered
- [ ] Edge cases covered

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r backend/requirements.txt
      - run: pip install -r backend/requirements-test.txt
      - run: pytest backend/tests/ -v
```

## Notes

- Some tests may skip if external services (OpenAI, Alpha Vantage) are unavailable
- Tests use mocked environment variables to avoid requiring real API keys
- Integration tests may require actual API keys for full functionality
- E2E tests require both frontend and backend to be running

## Troubleshooting

### Tests Failing

1. Check that all dependencies are installed
2. Verify environment variables are set (or mocked)
3. Ensure external services are accessible (if required)
4. Check test logs for specific error messages

### Import Errors

- Ensure you're running tests from the backend directory
- Check that `sys.path` includes the backend directory
- Verify all `__init__.py` files exist

### API Key Errors

- Use `mock_env_vars` fixture for tests
- Don't commit real API keys to test files
- Use environment variables or `.env.test` file

