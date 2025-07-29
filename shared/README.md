# 🔗 Shared - Código Compartido Entre Microservicios

## 📋 Descripción
Biblioteca de utilidades, modelos y middleware compartidos entre todos los microservicios del sistema LLM Wrapper Web para mantener consistencia y evitar duplicación de código.

## 🏗️ Estructura de Shared

```
shared/
├── README.md
├── __init__.py
├── auth/
│   ├── __init__.py
│   ├── middleware.py       # Middleware de autenticación
│   ├── decorators.py       # Decoradores para permisos
│   └── jwt_handler.py      # Manejo de JWT tokens
├── models/
│   ├── __init__.py
│   ├── base.py            # Modelos base de Pydantic
│   ├── user.py            # Modelos relacionados con usuarios
│   ├── conversation.py    # Modelos de conversaciones
│   ├── payment.py         # Modelos de pagos
│   └── response.py        # Modelos de respuestas API
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Configuración de logging
│   ├── validators.py      # Validadores comunes
│   ├── formatters.py      # Formatters de datos
│   ├── crypto.py          # Utilidades de encriptación
│   └── database.py        # Helpers de base de datos
├── exceptions/
│   ├── __init__.py
│   ├── base.py            # Excepciones base
│   ├── auth.py            # Excepciones de autenticación
│   ├── payment.py         # Excepciones de pagos
│   └── llm.py             # Excepciones de LLMs
└── config/
    ├── __init__.py
    ├── settings.py        # Configuraciones compartidas
    └── constants.py       # Constantes del sistema
```

## 🔐 Auth Middleware

### JWT Authentication Middleware
```python
# shared/auth/middleware.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from ..exceptions.auth import InvalidTokenException, ExpiredTokenException

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    async def verify_token(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """Verificar y decodificar JWT token"""
        token = credentials.credentials
        
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verificar campos requeridos
            if not payload.get("sub"):
                raise InvalidTokenException("Token missing subject")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException("Token has expired")
        except jwt.JWTError:
            raise InvalidTokenException("Invalid token")
    
    async def get_current_user(
        self, 
        token_payload: dict = Depends(verify_token)
    ) -> dict:
        """Obtener información del usuario actual"""
        return {
            "user_id": token_payload.get("sub"),
            "email": token_payload.get("email"),
            "role": token_payload.get("role", "free"),
            "permissions": token_payload.get("permissions", [])
        }

# Factory function para crear middleware
def create_auth_middleware(secret_key: str) -> AuthMiddleware:
    return AuthMiddleware(secret_key)
```

### Permission Decorators
```python
# shared/auth/decorators.py
from functools import wraps
from fastapi import HTTPException, status
from typing import List, Callable

def require_permissions(required_permissions: List[str]):
    """Decorador para requerir permisos específicos"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extraer usuario del contexto
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_permissions = current_user.get("permissions", [])
            
            # Verificar permisos
            for permission in required_permissions:
                if permission not in user_permissions and "*" not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission {permission} required"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_subscription(min_plan: str):
    """Decorador para requerir nivel mínimo de suscripción"""
    plan_hierarchy = {"free": 0, "premium": 1, "enterprise": 2}
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            user_plan = current_user.get("role", "free")
            
            if plan_hierarchy.get(user_plan, 0) < plan_hierarchy.get(min_plan, 0):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Subscription plan {min_plan} or higher required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 📊 Modelos Compartidos

### Base Models
```python
# shared/models/base.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class BaseDBModel(BaseModel):
    """Modelo base para entidades de base de datos"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BaseResponse(BaseModel):
    """Modelo base para respuestas de API"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseResponse):
    """Respuesta paginada"""
    data: list
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
```

### Response Models
```python
# shared/models/response.py
from typing import Any, Optional, Dict, List
from .base import BaseResponse

class SuccessResponse(BaseResponse):
    """Respuesta exitosa estándar"""
    data: Any

class ErrorResponse(BaseResponse):
    """Respuesta de error estándar"""
    success: bool = False
    error_code: str
    error_details: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    service: str
    status: str  # healthy, degraded, unhealthy
    version: str
    timestamp: datetime
    checks: Dict[str, Any] = {}

class ValidationErrorResponse(ErrorResponse):
    """Respuesta de error de validación"""
    error_code: str = "VALIDATION_ERROR"
    validation_errors: List[Dict[str, str]]
```

## 🛠️ Utilidades Compartidas

### Logger Configuration
```python
# shared/utils/logger.py
import logging
import sys
from datetime import datetime
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estructurados"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": getattr(record, 'service', 'unknown'),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar contexto adicional si existe
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'extra'):
            log_data['extra'] = record.extra
        
        return json.dumps(log_data)

def setup_logger(service_name: str, level: str = "INFO") -> logging.Logger:
    """Configurar logger para un microservicio"""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    
    # Agregar contexto del servicio
    logger = logging.LoggerAdapter(logger, {"service": service_name})
    
    return logger

# Factory function
def get_logger(service_name: str) -> logging.Logger:
    return setup_logger(service_name)
```

### Validators
```python
# shared/utils/validators.py
import re
from typing import Optional
from pydantic import validator

class CommonValidators:
    """Validadores comunes reutilizables"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validar fortaleza de contraseña"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValueError("Password must contain number")
        
        return password
    
    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """Validar formato de user ID"""
        if not user_id or len(user_id) < 1:
            raise ValueError("User ID cannot be empty")
        
        # Validar que sea UUID válido si es necesario
        pattern = r'^[a-f0-9-]{36}$'
        if not re.match(pattern, user_id):
            raise ValueError("Invalid user ID format")
        
        return user_id
    
    @staticmethod
    def validate_llm_model(model: str) -> str:
        """Validar nombre de modelo LLM"""
        valid_models = [
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
            "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
            "deepseek-chat", "deepseek-coder",
            "gemini-pro", "gemini-pro-vision"
        ]
        
        if model not in valid_models:
            raise ValueError(f"Invalid model. Must be one of: {valid_models}")
        
        return model
```

### Database Helpers
```python
# shared/utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from typing import Optional, Dict, Any
import os

class DatabaseManager:
    """Manager para conexiones de base de datos"""
    
    def __init__(self, mongodb_uri: str, database_name: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            
            # Test de conectividad
            await self.client.admin.command('ping')
            
        except PyMongoError as e:
            raise Exception(f"Failed to connect to MongoDB: {e}")
    
    async def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud de la base de datos"""
        try:
            result = await self.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": self.database_name,
                "ping_result": result
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Factory function
def create_database_manager(service_name: str) -> DatabaseManager:
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME", f"llm_wrapper_{service_name}")
    
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable is required")
    
    return DatabaseManager(mongodb_uri, database_name)
```

## ⚠️ Excepciones Compartidas

### Base Exceptions
```python
# shared/exceptions/base.py
from fastapi import HTTPException, status

class BaseServiceException(Exception):
    """Excepción base para todos los servicios"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)

class ValidationException(BaseServiceException):
    """Excepción de validación"""
    pass

class NotFoundExceptio(BaseServiceException):
    """Excepción de recurso no encontrado"""
    pass

class PermissionDeniedException(BaseServiceException):
    """Excepción de permisos insuficientes"""
    pass

# Convertir excepciones a HTTPException
def handle_service_exception(exc: BaseServiceException) -> HTTPException:
    """Convertir excepción de servicio a HTTP exception"""
    
    status_map = {
        "ValidationException": status.HTTP_400_BAD_REQUEST,
        "NotFoundException": status.HTTP_404_NOT_FOUND,
        "PermissionDeniedException": status.HTTP_403_FORBIDDEN,
        "InvalidTokenException": status.HTTP_401_UNAUTHORIZED,
        "ExpiredTokenException": status.HTTP_401_UNAUTHORIZED,
    }
    
    status_code = status_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )
```

## ⚙️ Configuración Compartida

### Settings
```python
# shared/config/settings.py
from pydantic import BaseSettings
from typing import List, Optional

class SharedSettings(BaseSettings):
    """Configuraciones compartidas entre servicios"""
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    MONGODB_URI: str
    
    # Redis
    REDIS_URL: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "structured"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 100
    
    class Config:
        env_file = ".env"

# Singleton para configuración
_settings = None

def get_settings() -> SharedSettings:
    global _settings
    if _settings is None:
        _settings = SharedSettings()
    return _settings
```

### Constants
```python
# shared/config/constants.py

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
```

## 📦 Uso en Microservicios

### Ejemplo de Integración
```python
# En cualquier microservicio
from shared.auth.middleware import create_auth_middleware
from shared.models.response import SuccessResponse, ErrorResponse
from shared.utils.logger import get_logger
from shared.config.settings import get_settings
from shared.exceptions.base import handle_service_exception

# Configuración del servicio
settings = get_settings()
logger = get_logger("chat-service")
auth_middleware = create_auth_middleware(settings.JWT_SECRET_KEY)

# En endpoints
@app.get("/protected", response_model=SuccessResponse)
async def protected_endpoint(
    current_user: dict = Depends(auth_middleware.get_current_user)
):
    logger.info("Protected endpoint accessed", extra={"user_id": current_user["user_id"]})
    return SuccessResponse(data={"message": "Access granted"})
```

---

**Ubicación**: `shared/`  
**Estado**: 🔄 En desarrollo  
**Próximo**: Implementar utilidades base y auth middleware 