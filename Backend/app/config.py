"""
Application configuration and settings.

This module defines the application settings using Pydantic BaseSettings,
which automatically loads values from environment variables.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All sensitive values should be set via environment variables or .env.local file.
    Default values are provided for local development only.
    """

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5433/growgent",
        description="PostgreSQL database connection URL (port 5433 for Growgent, 5432 for other instances)",
    )

    # API Keys - must be set via environment variables
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for MCP/agent functionality",
    )
    mapbox_token: str = Field(
        default="",
        description="Mapbox access token for map rendering",
    )
    noaa_api_key: Optional[str] = Field(
        default=None,
        description="NOAA API key for weather/fire data (optional)",
    )
    google_earth_engine_key: Optional[str] = Field(
        default=None,
        description="Google Earth Engine API key for NDVI data (optional)",
    )

    # Salesforce (optional)
    salesforce_client_id: Optional[str] = Field(
        default=None,
        description="Salesforce OAuth client ID",
    )
    salesforce_client_secret: Optional[str] = Field(
        default=None,
        description="Salesforce OAuth client secret",
    )

    # Redis (optional)
    redis_url: Optional[str] = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching",
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode (should be False in production)",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """
        Validate environment value.

        Args:
            v: Environment string value

        Returns:
            Validated environment string

        Raises:
            ValueError: If environment is not one of the allowed values
        """
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug(cls, v: bool, info) -> bool:
        """
        Ensure debug is False in production.

        Args:
            v: Debug boolean value
            info: Validation info containing other field values

        Returns:
            Validated debug boolean
        """
        if info.data.get("environment") == "production" and v:
            raise ValueError("debug must be False in production environment")
        return v


# Global settings instance
settings = Settings()
