"""
Modelos Pydantic compartidos entre microservicios
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List
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


class SuccessResponse(BaseResponse):
    """Respuesta exitosa estándar"""
    data: Any


class ErrorResponse(BaseResponse):
    """Respuesta de error estándar"""
    success: bool = False
    error_code: str
    error_details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(ErrorResponse):
    """Respuesta de error de validación"""
    error_code: str = "VALIDATION_ERROR"
    validation_errors: List[Dict[str, str]]


class HealthResponse(BaseModel):
    """Respuesta de health check"""
    service: str
    status: str  # healthy, degraded, unhealthy
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, Any] = {}


class PaginatedResponse(BaseResponse):
    """Respuesta paginada"""
    data: List[Any]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


# User Models
class UserBase(BaseModel):
    """Modelo base de usuario"""
    email: EmailStr
    name: str
    is_active: bool = True
    email_verified: bool = False


class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str


class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase, BaseDBModel):
    """Modelo completo de usuario"""
    password_hash: str
    subscription_status: str = "free"
    subscription_expires: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserInDB(User):
    """Usuario en base de datos"""
    password_hash: str


class UserResponse(UserBase):
    """Respuesta de usuario (sin datos sensibles)"""
    id: str
    subscription_status: str
    subscription_expires: Optional[datetime]
    created_at: datetime
    last_login: Optional[datetime]


# Auth Models
class Token(BaseModel):
    """Modelo de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Datos del token"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseModel):
    """Solicitud de login"""
    email: EmailStr
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    """Solicitud de registro"""
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    
    def passwords_match(self) -> bool:
        return self.password == self.confirm_password


# Subscription Models
class Subscription(BaseDBModel):
    """Modelo de suscripción"""
    user_id: str
    plan: str  # free, premium, enterprise
    status: str  # active, inactive, cancelled
    current_period_start: datetime
    current_period_end: datetime
    stripe_subscription_id: Optional[str] = None
    mercadopago_subscription_id: Optional[str] = None


# Conversation Models
class ConversationBase(BaseModel):
    """Modelo base de conversación"""
    title: str
    tags: List[str] = []
    category: Optional[str] = None
    is_favorite: bool = False
    is_archived: bool = False


class Conversation(ConversationBase, BaseDBModel):
    """Modelo completo de conversación"""
    user_id: str
    last_message_at: datetime
    message_count: int = 0
    total_tokens: int = 0
    models_used: List[str] = []
    retention_until: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class Message(BaseDBModel):
    """Modelo de mensaje"""
    conversation_id: str
    role: str  # user, assistant, system
    content: str
    model_used: Optional[str] = None
    tokens_used: int = 0
    cost_estimate: float = 0.0
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = {}
    parent_message_id: Optional[str] = None


# Chat Models
class ChatRequest(BaseModel):
    """Solicitud de chat"""
    message: str
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    """Respuesta de chat"""
    message: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float


class LLMStatus(BaseModel):
    """Estado de un modelo LLM"""
    provider: str
    model: str
    status: str  # online, offline, maintenance
    response_time_avg: float
    error_rate: float
    last_check: datetime = Field(default_factory=datetime.utcnow)


# Payment Models
class Transaction(BaseDBModel):
    """Modelo de transacción"""
    user_id: str
    subscription_id: str
    amount: float
    currency: str
    status: str  # pending, completed, failed, refunded
    payment_method: str  # stripe, mercadopago
    provider_transaction_id: str
    metadata: Dict[str, Any] = {}


class Invoice(BaseDBModel):
    """Modelo de factura"""
    user_id: str
    subscription_id: str
    amount_due: float
    amount_paid: float = 0.0
    currency: str
    status: str  # draft, open, paid, void, uncollectible
    due_date: datetime
    paid_at: Optional[datetime] = None
    invoice_pdf: Optional[str] = None
