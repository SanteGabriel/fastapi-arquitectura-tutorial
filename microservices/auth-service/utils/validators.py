"""
Validadores de datos de usuario
"""

import re
from typing import Optional, List
from fastapi import HTTPException, status


def validate_email(email: str) -> str:
    """Validar formato de email"""
    email = email.lower().strip()
    
    # Patrón básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_EMAIL",
                "message": "Invalid email format"
            }
        )
    
    # Validaciones adicionales
    if len(email) > 254:  # RFC 5321 limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "EMAIL_TOO_LONG",
                "message": "Email address is too long"
            }
        )
    
    # Verificar dominios bloqueados
    blocked_domains = {
        "example.com", "test.com", "localhost",
        "mailinator.com", "guerrillamail.com"
    }
    
    domain = email.split('@')[1]
    if domain in blocked_domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "BLOCKED_EMAIL_DOMAIN",
                "message": "Email domain is not allowed"
            }
        )
    
    return email


def validate_name(name: str) -> str:
    """Validar nombre de usuario"""
    name = name.strip()
    
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "NAME_REQUIRED",
                "message": "Name is required"
            }
        )
    
    if len(name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "NAME_TOO_SHORT",
                "message": "Name must be at least 2 characters long"
            }
        )
    
    if len(name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "NAME_TOO_LONG",
                "message": "Name must be less than 100 characters"
            }
        )
    
    # Verificar caracteres permitidos
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_NAME_CHARACTERS",
                "message": "Name contains invalid characters"
            }
        )
    
    return name


def validate_password(password: str) -> str:
    """Validar fortaleza de contraseña"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    # Verificar caracteres especiales
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Verificar contraseñas comunes
    common_passwords = {
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "1234567890", "abc123"
    }
    
    if password.lower() in common_passwords:
        errors.append("Password is too common, please choose a different one")
    
    # Verificar patrones secuenciales
    if re.search(r'(.)\1{3,}', password):  # 4 o más caracteres repetidos
        errors.append("Password should not contain repeated characters")
    
    if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
        errors.append("Password should not contain sequential numbers")
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "WEAK_PASSWORD",
                "message": "Password does not meet security requirements",
                "validation_errors": errors
            }
        )
    
    return password


def validate_user_data(name: str, email: str, password: str) -> dict:
    """Validar todos los datos de usuario"""
    validated_data = {
        "name": validate_name(name),
        "email": validate_email(email),
        "password": validate_password(password)
    }
    
    return validated_data


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitizar input de texto"""
    if not text:
        return ""
    
    # Remover caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Truncar si es muy largo
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remover espacios extra
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_subscription_status(status: str) -> str:
    """Validar estado de suscripción"""
    valid_statuses = {"free", "premium", "enterprise", "admin"}
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_SUBSCRIPTION_STATUS",
                "message": f"Invalid subscription status. Must be one of: {valid_statuses}"
            }
        )
    
    return status


def validate_user_id(user_id: str) -> str:
    """Validar formato de user ID"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "USER_ID_REQUIRED",
                "message": "User ID is required"
            }
        )
    
    # Validar que sea UUID válido
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, user_id.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_USER_ID",
                "message": "Invalid user ID format"
            }
        )
    
    return user_id
