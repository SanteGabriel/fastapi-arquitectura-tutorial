"""
Auth Service - Servicio de Autenticación
Puerto: 8001
"""

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta

# Imports locales
from models.user_models import UserRepository
from utils.password import PasswordManager
from utils.validators import validate_user_data

# Imports compartidos
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.models import (
    SuccessResponse, ErrorResponse, HealthResponse,
    LoginRequest, RegisterRequest, Token, UserResponse
)
from shared.auth_middleware import auth_middleware, get_current_user
from shared.database import init_database, close_database, get_database_manager
from shared.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    UserNotFoundException, handle_service_exception
)
from shared.config import get_settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events para inicialización y limpieza"""
    # Startup
    logger.info("🚀 Starting Auth Service...")
    try:
        await init_database()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Auth Service...")
    await close_database()
    logger.info("✅ Auth Service stopped")


# Crear aplicación FastAPI
app = FastAPI(
    title="LLM Wrapper - Auth Service",
    description="Servicio de autenticación y autorización con JWT",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Repositorios
user_repo = UserRepository()
password_manager = PasswordManager()


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para excepciones"""
    if isinstance(exc, (UserAlreadyExistsException, InvalidCredentialsException, 
                       UserNotFoundException)):
        http_exc = handle_service_exception(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )
    
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred"
        }
    )


# Health Check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servicio"""
    db_manager = get_database_manager()
    db_health = await db_manager.health_check()
    
    return HealthResponse(
        service="auth-service",
        status="healthy" if db_health["status"] == "healthy" else "degraded",
        version="1.0.0",
        checks={
            "database": db_health,
            "jwt_configured": bool(settings.JWT_SECRET_KEY)
        }
    )


# Endpoints de autenticación
@app.post("/register", response_model=SuccessResponse)
async def register_user(user_data: RegisterRequest):
    """Registrar nuevo usuario"""
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Validar datos
    if not user_data.passwords_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "PASSWORDS_MISMATCH",
                "message": "Passwords do not match"
            }
        )
    
    # Validar fortaleza de contraseña
    validate_user_data(user_data.name, user_data.email, user_data.password)
    
    # Verificar si el usuario ya existe
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise UserAlreadyExistsException("User with this email already exists")
    
    # Hash de la contraseña
    password_hash = password_manager.hash_password(user_data.password)
    
    # Crear usuario
    user_id = await user_repo.create_user({
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": password_hash,
        "subscription_status": "free",
        "is_active": True,
        "email_verified": False
    })
    
    logger.info(f"User registered successfully: {user_id}")
    return SuccessResponse(
        message="User registered successfully",
        data={"user_id": user_id, "email": user_data.email}
    )


@app.post("/login", response_model=SuccessResponse)
async def login_user(login_data: LoginRequest):
    """Iniciar sesión"""
    logger.info(f"Login attempt for email: {login_data.email}")
    
    # Buscar usuario
    user = await user_repo.get_by_email(login_data.email)
    if not user:
        raise InvalidCredentialsException("Invalid email or password")
    
    # Verificar contraseña
    if not password_manager.verify_password(login_data.password, user["password_hash"]):
        raise InvalidCredentialsException("Invalid email or password")
    
    # Verificar si el usuario está activo
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "ACCOUNT_DISABLED",
                "message": "Account is disabled"
            }
        )
    
    # Actualizar último login
    await user_repo.update_last_login(user["id"])
    
    # Crear tokens
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user.get("subscription_status", "free"),
        "permissions": _get_user_permissions(user.get("subscription_status", "free"))
    }
    
    access_token = auth_middleware.create_access_token(token_data)
    refresh_token = auth_middleware.create_refresh_token(token_data)
    
    logger.info(f"User logged in successfully: {user['id']}")
    return SuccessResponse(
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "subscription_status": user.get("subscription_status", "free")
            }
        }
    )


@app.post("/refresh", response_model=SuccessResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Renovar token de acceso"""
    logger.info(f"Token refresh for user: {current_user['user_id']}")
    
    # Verificar que el usuario aún existe y está activo
    user = await user_repo.get_by_id(current_user["user_id"])
    if not user or not user.get("is_active", False):
        raise UserNotFoundException("User not found or inactive")
    
    # Crear nuevo token
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user.get("subscription_status", "free"),
        "permissions": _get_user_permissions(user.get("subscription_status", "free"))
    }
    
    new_access_token = auth_middleware.create_access_token(token_data)
    
    return SuccessResponse(
        message="Token refreshed successfully",
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    )


@app.get("/me", response_model=SuccessResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    user = await user_repo.get_by_id(current_user["user_id"])
    if not user:
        raise UserNotFoundException("User not found")
    
    return SuccessResponse(
        message="User info retrieved successfully",
        data={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "subscription_status": user.get("subscription_status", "free"),
            "email_verified": user.get("email_verified", False),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login")
        }
    )


@app.put("/profile", response_model=SuccessResponse)
async def update_profile(
    user_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar perfil de usuario"""
    user_id = current_user["user_id"]
    
    # Filtrar campos permitidos para actualizar
    allowed_fields = ["name"]
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "NO_FIELDS_TO_UPDATE",
                "message": "No valid fields to update"
            }
        )
    
    success = await user_repo.update_user(user_id, update_data)
    if not success:
        raise UserNotFoundException("User not found")
    
    return SuccessResponse(
        message="Profile updated successfully",
        data=update_data
    )


@app.post("/logout", response_model=SuccessResponse)
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Cerrar sesión (principalmente para logs)"""
    logger.info(f"User logged out: {current_user['user_id']}")
    return SuccessResponse(
        message="Logout successful",
        data={}
    )


# Endpoint para validar tokens (usado por otros microservicios)
@app.post("/validate-token", response_model=SuccessResponse)
async def validate_token_external(current_user: dict = Depends(get_current_user)):
    """Validar token para otros microservicios"""
    return SuccessResponse(
        message="Token is valid",
        data={
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "role": current_user["role"],
            "permissions": current_user["permissions"]
        }
    )


# Helper functions
def _get_user_permissions(subscription_status: str) -> list:
    """Obtener permisos basados en el estado de suscripción"""
    permissions_map = {
        "free": ["chat:basic", "history:read"],
        "premium": ["chat:advanced", "history:full", "export:pdf"],
        "enterprise": ["chat:unlimited", "history:unlimited", "analytics:full"],
        "admin": ["*"]
    }
    return permissions_map.get(subscription_status, permissions_map["free"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
