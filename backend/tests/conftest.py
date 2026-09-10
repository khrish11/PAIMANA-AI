"""
Pytest configuration for PAIMANA-AI backend tests.

Defines markers for different test categories.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "db: marks tests as requiring PostgreSQL database connection"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow-running"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture
def db():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create a test client for API testing."""
    return TestClient(app)
