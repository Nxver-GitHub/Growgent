"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/growgent"
    
    # API Keys
    anthropic_api_key: str = ""
    mapbox_token: str = ""
    noaa_api_key: str = ""
    google_earth_engine_key: str = ""
    
    # Salesforce (optional)
    salesforce_client_id: str = ""
    salesforce_client_secret: str = ""
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False


settings = Settings()

