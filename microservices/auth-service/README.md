# 🔐 Auth Service - Servicio de Autenticación

## 📋 Descripción
Microservicio responsable de la autenticación, autorización y gestión de usuarios del sistema LLM Wrapper Web.

## 🏗️ Arquitectura del Servicio

```
┌─────────────────────────────────────────┐
│              AUTH SERVICE               │
│              Puerto: 8001               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Routes    │    │  Middleware │    │
│  │             │    │             │    │
│  │ /register   │◄──►│ JWT Manager │    │
│  │ /login      │    │ Rate Limit  │    │
│  │ /logout     │    │ Validation  │    │
│  │ /me         │    │             │    │
│  │ /refresh    │    │             │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Models    │    │    Utils    │    │
│  │             │    │             │    │
│  │ User        │    │ Hash Pass   │    │
│  │ Token       │    │ Validators  │    │
│  │ Session     │    │ Exceptions  │    │
│  └─────────────┘    └─────────────┘    │
│         │                              │
│         ▼                              │
│  ┌─────────────────────────────────┐   │
│  │         DATABASE                │   │
│  │      MongoDB Atlas              │   │
│  │                                 │   │
│  │ Collections:                    │   │
│  │ - users                         │   │
│  │ - sessions                      │   │
│  │ - subscriptions                 │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Funcionalidades

### Core Features
- **Registro de Usuarios**: Creación de cuentas con validación
- **Autenticación**: Login/Logout con JWT tokens
- **Autorización**: Verificación de permisos y roles
- **Gestión de Sesiones**: Control de sesiones activas
- **Suscripciones**: Manejo de planes (free, premium, enterprise)

### Endpoints Principales

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| POST | `/register` | Registro de nuevo usuario | ❌ |
| POST | `/login` | Iniciar sesión | ❌ |
| POST | `/logout` | Cerrar sesión | ✅ |
| GET | `/me` | Información del usuario actual | ✅ |
| POST | `/refresh` | Renovar token | ✅ |
| PUT | `/profile` | Actualizar perfil | ✅ |
| GET | `/subscription` | Estado de suscripción | ✅ |

## 📊 Modelos de Datos

### User Model
```python
class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    password_hash: str
    subscription_status: str  # free, premium, enterprise
    subscription_expires: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    email_verified: bool = False
```

### Token Model
```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

### Subscription Model
```python
class Subscription(BaseModel):
    user_id: str
    plan: str  # free, premium, enterprise
    status: str  # active, inactive, cancelled
    current_period_start: datetime
    current_period_end: datetime
    stripe_subscription_id: Optional[str]
    mercadopago_subscription_id: Optional[str]
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_auth
USERS_COLLECTION=users
SESSIONS_COLLECTION=sessions
SUBSCRIPTIONS_COLLECTION=subscriptions

# Security
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=1
```

### Dependencias (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
PyJWT==2.8.0
pymongo==4.6.0
motor==3.3.2
bcrypt==4.1.2
email-validator==2.1.0
slowapi==0.1.9
```

## 🔐 Seguridad

### Medidas Implementadas
- **Hash de Contraseñas**: bcrypt con salt rounds
- **JWT Tokens**: Firmados con HS256
- **Rate Limiting**: Por IP y por usuario
- **Validación de Input**: Pydantic models
- **Timeout de Sesiones**: Configurables
- **Bloqueo por Intentos**: Anti-brute force

### Roles y Permisos
```python
class UserRole(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

# Permisos por rol
ROLE_PERMISSIONS = {
    "free": ["chat:basic", "history:read"],
    "premium": ["chat:advanced", "history:full", "export:pdf"],
    "enterprise": ["chat:unlimited", "history:unlimited", "analytics:full"],
    "admin": ["*"]  # Todos los permisos
}
```

## 📱 Integración con otros Servicios

### Comunicación Inter-Servicios
```python
# Middleware para validar tokens en otros servicios
@app.middleware("http")
async def validate_token_middleware(request: Request, call_next):
    # Validación de JWT para requests entre servicios
    pass

# Endpoint para validación externa
@app.post("/validate-token")
async def validate_token_external(token: str):
    # Usado por otros microservicios para validar tokens
    return {"valid": True, "user_id": "...", "role": "..."}
```

## 🧪 Testing

### Casos de Prueba
- ✅ Registro exitoso de usuario
- ✅ Login con credenciales válidas
- ❌ Login con credenciales inválidas
- ✅ Renovación de token
- ❌ Token expirado
- ✅ Rate limiting
- ✅ Validación de roles

### Comandos de Testing
```bash
# Ejecutar tests
pytest tests/ -v

# Coverage
pytest --cov=. tests/

# Tests específicos
pytest tests/test_auth.py -v
```

## 🚀 Desarrollo Local

### Setup Inicial
```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Ejecutar servicio
uvicorn main:app --reload --port 8001
```

### Health Check
```bash
curl http://localhost:8001/health
```

## 📈 Monitoreo y Logs

### Métricas Clave
- Tiempo de respuesta de autenticación
- Tasa de registros exitosos
- Intentos de login fallidos
- Tokens activos
- Distribución de roles de usuario

### Logging
```python
import logging

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Logs de eventos importantes
logger.info(f"User {user_id} logged in successfully")
logger.warning(f"Failed login attempt for {email}")
logger.error(f"Token validation failed: {error}")
```

---

**Puerto**: 8001  
**Estado**: 🔄 En desarrollo  
**Próximo**: Implementar JWT y conexión MongoDB 