"""
Middleware de autenticación JWT compartido
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
import logging

from .exceptions import InvalidTokenException, ExpiredTokenException, InsufficientPermissionsException
from .config import get_settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.JWT_SECRET_KEY
        self.algorithm = self.settings.JWT_ALGORITHM
        
    async def verify_token(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
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
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise ExpiredTokenException("Token has expired")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException("Token has expired")
        except jwt.JWTError as e:
            logger.error(f"JWT Error: {e}")
            raise InvalidTokenException("Invalid token")
    
    async def get_current_user(
        self, 
        token_payload: Dict[str, Any] = Depends(verify_token)
    ) -> Dict[str, Any]:
        """Obtener información del usuario actual"""
        return {
            "user_id": token_payload.get("sub"),
            "email": token_payload.get("email"),
            "name": token_payload.get("name"),
            "role": token_payload.get("role", "free"),
            "permissions": token_payload.get("permissions", []),
            "subscription_status": token_payload.get("subscription_status", "free"),
        }

    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crear token de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


# Instancia global del middleware
auth_middleware = AuthMiddleware()


# Dependencias para FastAPI
async def get_current_user(
    token_payload: Dict[str, Any] = Depends(auth_middleware.verify_token)
) -> Dict[str, Any]:
    """Dependencia para obtener usuario actual"""
    return await auth_middleware.get_current_user(token_payload)


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Dependencia para obtener usuario activo"""
    # Aquí podrías agregar verificaciones adicionales
    # como si el usuario está activo, verificado, etc.
    return current_user


# Decoradores para permisos
def require_permissions(required_permissions: list):
    """Decorador para requerir permisos específicos"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extraer usuario del contexto
            current_user = kwargs.get("current_user")
            if not current_user:
                raise InvalidTokenException("Authentication required")
            
            user_permissions = current_user.get("permissions", [])
            
            # Verificar permisos
            for permission in required_permissions:
                if permission not in user_permissions and "*" not in user_permissions:
                    raise InsufficientPermissionsException(
                        f"Permission {permission} required"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_subscription(min_plan: str):
    """Decorador para requerir nivel mínimo de suscripción"""
    plan_hierarchy = {"free": 0, "premium": 1, "enterprise": 2, "admin": 3}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise InvalidTokenException("Authentication required")
                
            user_plan = current_user.get("role", "free")
            
            if plan_hierarchy.get(user_plan, 0) < plan_hierarchy.get(min_plan, 0):
                raise InsufficientPermissionsException(
                    f"Subscription plan {min_plan} or higher required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Función para validar token sin dependencias FastAPI
def validate_token(token: str) -> Dict[str, Any]:
    """Validar token JWT directamente"""
    try:
        settings = get_settings()
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verificar expiración
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            raise ExpiredTokenException("Token has expired")
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException("Token has expired")
    except jwt.JWTError:
        raise InvalidTokenException("Invalid token")
