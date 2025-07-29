# 🤖 Chat Service - Servicio de Integración LLMs

## 📋 Descripción
Microservicio responsable de la integración con múltiples proveedores de LLMs (DeepSeek, Claude, ChatGPT, Gemini) para el sistema LLM Wrapper Web.

## 🏗️ Arquitectura del Servicio

```
┌─────────────────────────────────────────┐
│              CHAT SERVICE               │
│              Puerto: 8002               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Routes    │    │  Middleware │    │
│  │             │    │             │    │
│  │ /chat       │◄──►│ Auth Check  │    │
│  │ /models     │    │ Rate Limit  │    │
│  │ /stream     │    │ Input Valid │    │
│  │ /history    │    │ Token Count │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │LLM Providers│    │ LLM Router  │    │
│  │             │    │             │    │
│  │ OpenAI      │◄──►│ Load Balancer│   │
│  │ Claude      │    │ Fallback    │    │
│  │ DeepSeek    │    │ Selection   │    │
│  │ Gemini      │    │             │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  Response   │    │   Utils     │    │
│  │  Processor  │    │             │    │
│  │             │    │ Token Count │    │
│  │ Streaming   │    │ Sanitizer   │    │
│  │ Formatting  │    │ Validator   │    │
│  │ Error Handle│    │ Metrics     │    │
│  └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────┘
```

## 🚀 Funcionalidades

### Core Features
- **Multi-LLM Integration**: Soporte para 4 proveedores principales
- **Smart Routing**: Selección automática o manual de LLM
- **Streaming Responses**: Respuestas en tiempo real
- **Fallback System**: Cambio automático si un LLM falla
- **Rate Limiting**: Control por suscripción de usuario
- **Token Counting**: Conteo preciso de tokens

### Endpoints Principales

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| POST | `/chat` | Enviar mensaje al LLM | ✅ |
| POST | `/chat/stream` | Chat con streaming | ✅ |
| GET | `/models` | Listar LLMs disponibles | ✅ |
| GET | `/models/{model}/status` | Estado de un LLM | ✅ |
| POST | `/chat/batch` | Procesamiento por lotes | ✅ |
| GET | `/usage` | Estadísticas de uso | ✅ |

## 🤖 LLMs Integrados

### OpenAI (ChatGPT)
```python
class OpenAIProvider:
    models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    max_tokens = 128000
    supports_streaming = True
    cost_per_1k_tokens = {"input": 0.01, "output": 0.03}
```

### Anthropic (Claude)
```python
class ClaudeProvider:
    models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    max_tokens = 200000
    supports_streaming = True
    cost_per_1k_tokens = {"input": 0.015, "output": 0.075}
```

### DeepSeek
```python
class DeepSeekProvider:
    models = ["deepseek-chat", "deepseek-coder"]
    max_tokens = 32000
    supports_streaming = True
    cost_per_1k_tokens = {"input": 0.0014, "output": 0.0028}
```

### Google (Gemini)
```python
class GeminiProvider:
    models = ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
    max_tokens = 32768
    supports_streaming = True
    cost_per_1k_tokens = {"input": 0.0005, "output": 0.0015}
```

## 📊 Modelos de Datos

### Chat Request
```python
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # Auto-select si es None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
```

### Chat Response
```python
class ChatResponse(BaseModel):
    message: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    conversation_id: str
    timestamp: datetime
    processing_time: float
```

### LLM Status
```python
class LLMStatus(BaseModel):
    provider: str
    model: str
    status: str  # online, offline, maintenance
    response_time_avg: float
    error_rate: float
    last_check: datetime
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# LLM API Keys
OPENAI_API_KEY=sk-your-openai-api-key
CLAUDE_API_KEY=sk-ant-your-claude-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
GEMINI_API_KEY=your-gemini-api-key

# LLM Configuration
DEFAULT_LLM=openai
MAX_TOKENS_DEFAULT=4000
TEMPERATURE_DEFAULT=0.7
ENABLE_STREAMING=true

# Rate Limiting (por plan de suscripción)
FREE_REQUESTS_PER_HOUR=50
PREMIUM_REQUESTS_PER_HOUR=500
ENTERPRISE_REQUESTS_PER_HOUR=5000

# Failover Configuration
ENABLE_FALLBACK=true
FALLBACK_ORDER=openai,claude,deepseek,gemini
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=2

# Monitoring
ENABLE_METRICS=true
LOG_REQUESTS=true
LOG_RESPONSES=false  # Para privacidad
```

### Dependencias (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
openai==1.6.1
anthropic==0.8.1
httpx==0.26.0
aiohttp==3.9.1
tiktoken==0.5.2
google-generativeai==0.3.2
tenacity==8.2.3
slowapi==0.1.9
prometheus-client==0.19.0
```

## 🔀 LLM Router Logic

### Auto-Selection Algorithm
```python
async def select_optimal_llm(
    message: str, 
    user_subscription: str,
    conversation_context: Optional[List]
) -> str:
    """
    Lógica de selección automática de LLM basada en:
    - Tipo de consulta (código, conversación, análisis)
    - Plan de suscripción del usuario
    - Estado actual de los LLMs
    - Costos por token
    - Historial de respuestas exitosas
    """
    
    # Análisis del tipo de consulta
    if is_code_related(message):
        return "deepseek"  # Mejor para código
    elif is_long_conversation(conversation_context):
        return "claude"  # Mejor contexto largo
    elif user_subscription == "free":
        return "deepseek"  # Más económico
    else:
        return "openai"  # Default confiable
```

### Fallback Strategy
```python
async def handle_llm_fallback(
    request: ChatRequest,
    failed_provider: str,
    error: Exception
) -> ChatResponse:
    """
    Sistema de fallback cuando un LLM falla:
    1. Log del error
    2. Seleccionar siguiente LLM en orden
    3. Ajustar parámetros si es necesario
    4. Reintentar con nuevo proveedor
    """
    fallback_order = get_fallback_order(failed_provider)
    
    for next_provider in fallback_order:
        if await is_provider_healthy(next_provider):
            return await send_to_llm(request, next_provider)
    
    raise AllProvidersUnavailableException()
```

## 📈 Rate Limiting & Quotas

### Por Plan de Suscripción
```python
RATE_LIMITS = {
    "free": {
        "requests_per_hour": 50,
        "tokens_per_day": 10000,
        "available_models": ["deepseek", "gemini"]
    },
    "premium": {
        "requests_per_hour": 500,
        "tokens_per_day": 100000,
        "available_models": ["openai", "claude", "deepseek", "gemini"]
    },
    "enterprise": {
        "requests_per_hour": 5000,
        "tokens_per_day": 1000000,
        "available_models": ["*"],
        "priority_queue": True
    }
}
```

## 🔒 Seguridad y Validación

### Input Sanitization
```python
async def sanitize_user_input(message: str) -> str:
    """
    Sanitización de inputs para prevenir:
    - Injection prompts
    - Contenido malicioso
    - Prompts que violen ToS de LLMs
    """
    # Remover caracteres peligrosos
    # Detectar prompt injection
    # Validar longitud
    # Filtrar contenido inapropiado
    return cleaned_message
```

### Content Filtering
```python
BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "act as if you are",
    "pretend to be",
    # ... más patrones de prompt injection
]

async def validate_content(message: str) -> bool:
    """Validar que el contenido cumple políticas"""
    return not any(pattern in message.lower() for pattern in BLOCKED_PATTERNS)
```

## 🧪 Testing

### Unit Tests
```bash
# Test individual LLM providers
pytest tests/test_providers/ -v

# Test routing logic
pytest tests/test_router.py -v

# Test rate limiting
pytest tests/test_rate_limiting.py -v

# Test streaming
pytest tests/test_streaming.py -v
```

### Integration Tests
```bash
# Test con LLMs reales (requiere API keys)
pytest tests/integration/ -v --api-keys

# Mock tests (sin API keys)
pytest tests/integration/ -v --mock
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
# Editar .env con tus API keys

# Ejecutar servicio
uvicorn main:app --reload --port 8002
```

### Health Check
```bash
curl http://localhost:8002/health
curl http://localhost:8002/models
```

## 📊 Monitoreo y Métricas

### Métricas Clave
- Requests por segundo por LLM
- Tiempo de respuesta promedio
- Tasa de errores por proveedor
- Tokens consumidos por usuario
- Costos por LLM
- Uso de fallbacks

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

llm_requests_total = Counter("llm_requests_total", "Total requests", ["provider", "model"])
llm_response_time = Histogram("llm_response_time_seconds", "Response time", ["provider"])
llm_tokens_used = Counter("llm_tokens_used_total", "Tokens used", ["provider", "user"])
llm_errors_total = Counter("llm_errors_total", "Total errors", ["provider", "error_type"])
```

---

**Puerto**: 8002  
**Estado**: 🔄 En desarrollo  
**Próximo**: Implementar integración con OpenAI 