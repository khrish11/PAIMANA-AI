"""
Pytest configuration for PAIMANA-AI backend tests.

Defines markers for different test categories.
"""
import pytest


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
