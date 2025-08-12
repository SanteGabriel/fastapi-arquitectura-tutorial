"""
Excepciones personalizadas del sistema
"""

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


class NotFoundException(BaseServiceException):
    """Excepción de recurso no encontrado"""
    pass


class PermissionDeniedException(BaseServiceException):
    """Excepción de permisos insuficientes"""
    pass


class InvalidTokenException(BaseServiceException):
    """Excepción de token inválido"""
    pass


class ExpiredTokenException(BaseServiceException):
    """Excepción de token expirado"""
    pass


class UserNotFoundException(NotFoundException):
    """Usuario no encontrado"""
    pass


class UserAlreadyExistsException(BaseServiceException):
    """Usuario ya existe"""
    pass


class InvalidCredentialsException(BaseServiceException):
    """Credenciales inválidas"""
    pass


class InsufficientPermissionsException(PermissionDeniedException):
    """Permisos insuficientes"""
    pass


class RateLimitExceededException(BaseServiceException):
    """Límite de rate excedido"""
    pass


class LLMProviderException(BaseServiceException):
    """Excepción del proveedor LLM"""
    pass


class DatabaseConnectionException(BaseServiceException):
    """Excepción de conexión a base de datos"""
    pass


class RedisConnectionException(BaseServiceException):
    """Excepción de conexión a Redis"""
    pass


class PaymentException(BaseServiceException):
    """Excepción de pago"""
    pass


class SubscriptionException(BaseServiceException):
    """Excepción de suscripción"""
    pass


# Convertir excepciones a HTTPException
def handle_service_exception(exc: BaseServiceException) -> HTTPException:
    """Convertir excepción de servicio a HTTP exception"""
    
    status_map = {
        "ValidationException": status.HTTP_400_BAD_REQUEST,
        "NotFoundException": status.HTTP_404_NOT_FOUND,
        "UserNotFoundException": status.HTTP_404_NOT_FOUND,
        "PermissionDeniedException": status.HTTP_403_FORBIDDEN,
        "InsufficientPermissionsException": status.HTTP_403_FORBIDDEN,
        "InvalidTokenException": status.HTTP_401_UNAUTHORIZED,
        "ExpiredTokenException": status.HTTP_401_UNAUTHORIZED,
        "InvalidCredentialsException": status.HTTP_401_UNAUTHORIZED,
        "UserAlreadyExistsException": status.HTTP_409_CONFLICT,
        "RateLimitExceededException": status.HTTP_429_TOO_MANY_REQUESTS,
        "LLMProviderException": status.HTTP_503_SERVICE_UNAVAILABLE,
        "DatabaseConnectionException": status.HTTP_503_SERVICE_UNAVAILABLE,
        "RedisConnectionException": status.HTTP_503_SERVICE_UNAVAILABLE,
        "PaymentException": status.HTTP_402_PAYMENT_REQUIRED,
        "SubscriptionException": status.HTTP_402_PAYMENT_REQUIRED,
    }
    
    status_code = status_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )
