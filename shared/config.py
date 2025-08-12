"""
Configuraciones compartidas entre microservicios
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class SharedSettings(BaseSettings):
    """Configuraciones compartidas entre servicios"""
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    MONGODB_URI: str
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "structured"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 100
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"


# User roles
class UserRoles:
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


# LLM Providers
class LLMProviders:
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"


# Subscription Plans
class SubscriptionPlans:
    FREE = {
        "name": "free",
        "price": 0.00,
        "requests_per_hour": 50,
        "tokens_per_day": 10000,
        "models": [LLMProviders.DEEPSEEK, LLMProviders.GEMINI]
    }
    
    PREMIUM = {
        "name": "premium", 
        "price": 19.99,
        "requests_per_hour": 500,
        "tokens_per_day": 100000,
        "models": ["*"]
    }
    
    ENTERPRISE = {
        "name": "enterprise",
        "price": 99.99,
        "requests_per_hour": 5000,
        "tokens_per_day": 1000000,
        "models": ["*"]
    }


# HTTP Status Messages
class StatusMessages:
    SUCCESS = "Operation completed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Insufficient permissions"
    VALIDATION_ERROR = "Validation failed"


# Singleton para configuración
_settings = None

def get_settings() -> SharedSettings:
    global _settings
    if _settings is None:
        _settings = SharedSettings()
    return _settings
