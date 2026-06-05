"""Pytest fixtures for TuringMate backend tests."""
import os
import sys
import pytest
from unittest.mock import MagicMock

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings


@pytest.fixture
def mock_db_session():
    """Provides a mocked SQLAlchemy session."""
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.refresh = MagicMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def test_settings():
    """Override settings for test environment."""
    settings.SECRET_KEY = "test-secret-key-for-testing-only"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60
    return settings


@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "password": "TestPass123!",
        "name": "测试用户",
        "email": "test@example.com",
    }
