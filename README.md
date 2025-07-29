# LLM Wrapper Web - Microservicios con FastAPI

## 📋 PLANIFICACIÓN DEL PROYECTO

### 🎯 **Objetivo Principal**
Crear un wrapper web de LLMs con arquitectura de microservicios usando FastAPI para integrar múltiples proveedores de IA.

### 🚀 **Características Principales**

- **🤖 Chatbot Multi-LLM**: DeepSeek, Claude, ChatGPT y Gemini
- **💳 Sistema de Pagos**: Stripe Sandbox y Mercado Pago Sandbox  
- **📚 Historial Persistente**: MongoDB Atlas para conversaciones
- **⚡ Caché Inteligente**: Redis Cloud para optimización
- **🔐 Autenticación Segura**: JWT con gestión de suscripciones
- **🎨 Frontend Moderno**: React/Next.js con TypeScript

### 🏗️ **Arquitectura de Microservicios**

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                             │
│              (React/Next.js)                            │
│                  Puerto: 3000                           │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   API GATEWAY                           │
│              (Nginx/FastAPI Gateway)                    │
│                  Puerto: 8000                           │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│AUTH SERVICE │    │CHAT SERVICE │    │PAY SERVICE  │
│ Puerto: 8001│    │ Puerto: 8002│    │ Puerto: 8003│
└─────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│HISTORY SVC  │    │CACHE SERVICE│    │   SHARED    │
│ Puerto: 8004│    │ Puerto: 6379│    │  UTILITIES  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 📦 **Microservicios Detallados**

| Servicio | Puerto | Responsabilidad | Tecnologías |
|----------|--------|----------------|-------------|
| **auth-service** | 8001 | Autenticación y autorización | FastAPI, JWT, MongoDB |
| **chat-service** | 8002 | Integración con LLMs | FastAPI, APIs de IA |
| **payment-service** | 8003 | Procesamiento de pagos | FastAPI, Stripe, MercadoPago |
| **history-service** | 8004 | Gestión del historial | FastAPI, MongoDB Atlas |
| **cache-service** | 6379 | Caché y sesiones | Redis Cloud |

### 📁 **Estructura del Proyecto**

```
ArquitecturaTutorial/
├── frontend/                    # React/Next.js frontend
│   ├── package.json
│   ├── .env.local
│   ├── src/
│   └── public/
├── microservices/
│   ├── auth-service/           # Autenticación y autorización
│   │   ├── .venv/
│   │   ├── .env
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── models/
│   │   └── utils/
│   ├── chat-service/           # Integración con LLMs
│   │   ├── .venv/
│   │   ├── .env
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── llm_providers/
│   │   └── utils/
│   ├── payment-service/        # Stripe y Mercado Pago
│   │   ├── .venv/
│   │   ├── .env
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── stripe_handler.py
│   │   └── mercadopago_handler.py
│   ├── history-service/        # MongoDB para historial
│   │   ├── .venv/
│   │   ├── .env
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── models/
│   └── cache-service/          # Redis para caché
│       ├── README.md
│       ├── redis_config.py
│       └── utils.py
├── shared/                     # Código compartido
│   ├── README.md
│   ├── auth_middleware.py
│   ├── response_models.py
│   └── utils.py
├── docker-compose.yml          # Para futuro desarrollo
└── README.md
```

### 🛠️ **Tecnologías por Componente**

#### Backend
- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Autenticación**: JWT, PassLib
- **Base de Datos**: MongoDB Atlas
- **Caché**: Redis Cloud
- **Pagos**: Stripe, MercadoPago

#### Frontend
- **Framework**: React/Next.js 14+
- **Lenguaje**: TypeScript
- **Styling**: Tailwind CSS
- **Estado**: Zustand/Redux Toolkit
- **HTTP**: Axios

#### LLMs Integrados
- **DeepSeek**: API REST
- **Claude**: Anthropic API
- **ChatGPT**: OpenAI API
- **Gemini**: Google AI API

### 🔧 **Configuración de Entornos**

Cada microservicio tiene su propio entorno virtual (.venv) y archivo .env:

#### AUTH-SERVICE (.env)
```env
JWT_SECRET_KEY=your_jwt_secret_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### CHAT-SERVICE (.env)
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
DEFAULT_LLM=openai
MAX_TOKENS=4000
```

#### PAYMENT-SERVICE (.env)
```env
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_public
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
MERCADOPAGO_ACCESS_TOKEN=your_mp_access_token
MERCADOPAGO_WEBHOOK_SECRET=your_mp_webhook_secret
```

#### HISTORY-SERVICE (.env)
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_history
COLLECTION_NAME=conversations
```

#### CACHE-SERVICE (.env)
```env
REDIS_URL=redis://username:password@redis-cloud-url:port
CACHE_TTL=3600
SESSION_TTL=86400
```

### 🚀 **Plan de Implementación (Fases 1-9)**

1. **Fase 1**: ✅ Estructura base y documentación
2. **Fase 2**: 🔄 Auth Service con JWT y MongoDB
3. **Fase 3**: 🔄 Chat Service con OpenAI (primer LLM)
4. **Fase 4**: 🔄 History Service con MongoDB
5. **Fase 5**: 🔄 Integrar todos los LLMs (DeepSeek, Claude, Gemini)
6. **Fase 6**: 🔄 Frontend básico con React/Next.js
7. **Fase 7**: 🔄 Cache Service con Redis
8. **Fase 8**: 🔄 Payment Service (Stripe + MercadoPago)
9. **Fase 9**: 🔄 Frontend completo y UX optimizada

### 📚 **Documentación por Microservicio**

Cada microservicio incluye:
- **README.md**: Arquitectura específica del servicio
- **requirements.txt**: Dependencias Python
- **models/**: Modelos Pydantic
- **utils/**: Utilidades específicas
- **.env.example**: Plantilla de variables de entorno

### ⚡ **Comandos de Desarrollo**

```bash
# Activar entorno virtual por servicio
cd microservices/auth-service && source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servicio individual
uvicorn main:app --reload --port 8001

# Ejecutar todos los servicios (futuro con Docker)
docker-compose up -d
```

### 🔐 **Consideraciones de Seguridad**

- Todas las API keys se configuran en archivos .env
- JWT para autenticación stateless
- Validación de entrada con Pydantic
- Rate limiting por usuario/suscripción
- HTTPS en producción
- Sanitización de inputs para LLMs

---

**Estado**: 🔄 En desarrollo - Fase 1 completada
**Próximo**: Implementar Auth Service (Fase 2)
