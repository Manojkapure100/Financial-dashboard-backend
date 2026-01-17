"""
Configuration settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    app_name: str = "Financial Dashboard"
    debug: bool = False
    api_version: str = "v1"

    class Config:
        env_file = ".env"


settings = Settings()
