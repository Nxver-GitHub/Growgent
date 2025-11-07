"""
Tests for application configuration.

Tests cover settings validation and environment variable loading.
"""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_default_values() -> None:
    """
    Test that settings have appropriate default values for development.
    """
    settings = Settings()
    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.database_url is not None


def test_settings_environment_validation() -> None:
    """
    Test that environment validation rejects invalid values.
    """
    with pytest.raises(ValidationError):
        Settings(environment="invalid")


def test_settings_production_debug_validation() -> None:
    """
    Test that debug cannot be True in production environment.
    """
    with pytest.raises(ValidationError):
        Settings(environment="production", debug=True)


def test_settings_production_debug_allowed_false() -> None:
    """
    Test that debug can be False in production.
    """
    settings = Settings(environment="production", debug=False)
    assert settings.environment == "production"
    assert settings.debug is False

