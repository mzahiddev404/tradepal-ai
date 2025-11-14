"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "message": "Hello, how are you?",
        "history": []
    }

@pytest.fixture
def sample_stock_symbol():
    """Sample stock symbol for testing."""
    return "TSLA"

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test-key")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")


