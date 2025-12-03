"""
Core configuration module using Pydantic Settings.
Manages environment variables and application configuration.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "SafeLift-AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./safelift.db",
        description="Database connection URL"
    )
    
    # JWT Authentication
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token generation (min 32 characters)"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    
    # Safety Rules Engine
    IMPACT_THRESHOLD_G: float = 2.5  # G-force threshold for impact detection
    DANGEROUS_SPEED_KMH: float = 25.0  # Speed threshold in km/h
    MAST_TILT_THRESHOLD_DEG: float = 15.0  # Mast tilt angle threshold
    BRAKING_FORCE_THRESHOLD_G: float = 1.5  # Braking force threshold
    PROXIMITY_DANGER_METERS: float = 3.0  # Proximity danger distance
    
    # Working hours (for outside-hours detection)
    WORK_START_HOUR: int = 6  # 6 AM
    WORK_END_HOUR: int = 22  # 10 PM
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure DATABASE_URL is properly formatted."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        

# Global settings instance
settings = Settings()
