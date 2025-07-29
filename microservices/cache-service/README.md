# ⚡ Cache Service - Servicio de Caché

## 📋 Descripción
Microservicio responsable de la gestión de caché, sesiones temporales y optimización de rendimiento usando Redis Cloud para el sistema LLM Wrapper Web.

## 🏗️ Arquitectura del Servicio

```
┌─────────────────────────────────────────┐
│             CACHE SERVICE               │
│              Puerto: 6379               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Redis Utils │    │ Cache Manager│   │
│  │             │    │             │    │
│  │ Connection  │◄──►│ TTL Manager │    │
│  │ Pool        │    │ Eviction    │    │
│  │ Health Check│    │ Compression │    │
│  │ Monitoring  │    │ Serializers │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  Sessions   │    │ LLM Cache   │    │
│  │  Manager    │    │  Manager    │    │
│  │             │    │             │    │
│  │ User Auth   │    │ Responses   │    │
│  │ Temp Data   │    │ Embeddings  │    │
│  │ Rate Limits │    │ Completions │    │
│  │ Preferences │    │ Models Info │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Analytics   │    │   Utils     │    │
│  │  Cache      │    │             │    │
│  │             │    │ Validators  │    │
│  │ Metrics     │    │ Formatters  │    │
│  │ Counters    │    │ Encryption  │    │
│  │ Aggregation │    │ Logs        │    │
│  └─────────────┘    └─────────────┘    │
│         │                              │
│         ▼                              │
│  ┌─────────────────────────────────┐   │
│  │         REDIS CLOUD             │   │
│  │                                 │   │
│  │ Databases:                      │   │
│  │ - 0: Sessions & Auth            │   │
│  │ - 1: LLM Responses Cache        │   │
│  │ - 2: Rate Limiting              │   │
│  │ - 3: Analytics & Metrics        │   │
│  │ - 4: Temporary Data             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Funcionalidades

### Core Features
- **Session Management**: Gestión de sesiones de usuario
- **LLM Response Caching**: Cache inteligente de respuestas IA
- **Rate Limiting**: Control de límites por usuario/plan
- **Analytics Cache**: Datos agregados y métricas temporales
- **Temporary Storage**: Almacenamiento temporal para exports
- **Health Monitoring**: Monitoreo de Redis y conexiones

### Casos de Uso Principales

| Componente | Descripción | TTL | Base de Datos |
|------------|-------------|-----|---------------|
| **User Sessions** | Tokens JWT, preferencias | 24h | DB 0 |
| **LLM Cache** | Respuestas de IA repetidas | 1-7d | DB 1 |
| **Rate Limits** | Contadores por usuario | 1h-1d | DB 2 |
| **Analytics** | Métricas agregadas | 1h-30d | DB 3 |
| **Temp Files** | Exports, uploads | 1-24h | DB 4 |

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# Redis Configuration
REDIS_URL=redis://username:password@redis-cloud-url:port
REDIS_PASSWORD=your_redis_password
REDIS_SSL=true
REDIS_MAX_CONNECTIONS=20
REDIS_RETRY_ON_TIMEOUT=true

# Cache TTL Settings (seconds)
SESSION_TTL=86400           # 24 hours
LLM_CACHE_TTL=604800       # 7 days
RATE_LIMIT_TTL=3600        # 1 hour
ANALYTICS_TTL=2592000      # 30 days
TEMP_DATA_TTL=86400        # 24 hours

# Performance
ENABLE_COMPRESSION=true
COMPRESSION_THRESHOLD=1024  # bytes
MAX_MEMORY_POLICY=allkeys-lru
ENABLE_PIPELINE=true
PIPELINE_SIZE=100

# Monitoring
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30   # seconds
ALERT_ON_HIGH_MEMORY=true
MEMORY_THRESHOLD_PERCENT=80
```

### Dependencias
```
redis==5.0.1
aioredis==2.0.1
hiredis==2.2.3
pydantic==2.5.0
ujson==5.8.0
zstandard==0.22.0
prometheus-client==0.19.0
```

## 💾 Estructura de Datos Redis

### Database 0: Sessions & Auth
```python
# Sesiones de usuario
f"session:{user_id}" = {
    "token": "jwt_token_hash",
    "user_data": {...},
    "last_activity": timestamp,
    "permissions": [...]
}

# Tokens blacklist
f"blacklist:{token_hash}" = timestamp

# Preferencias de usuario
f"user_prefs:{user_id}" = {
    "default_llm": "openai",
    "temperature": 0.7,
    "theme": "dark"
}
```

### Database 1: LLM Response Cache
```python
# Cache de respuestas LLM
f"llm_cache:{hash}" = {
    "response": "cached_response",
    "model": "gpt-4",
    "tokens": 150,
    "timestamp": timestamp
}

# Cache de embeddings
f"embedding:{text_hash}" = [0.1, 0.2, ..., 0.n]

# Información de modelos
f"model_info:{provider}:{model}" = {
    "status": "online",
    "last_check": timestamp,
    "avg_response_time": 1.2
}
```

### Database 2: Rate Limiting
```python
# Contadores por usuario
f"rate_limit:{user_id}:hour" = count
f"rate_limit:{user_id}:day" = count

# Límites por IP
f"ip_limit:{ip}:minute" = count

# Tokens usados por usuario
f"tokens:{user_id}:day" = total_tokens
```

### Database 3: Analytics
```python
# Métricas agregadas por hora
f"metrics:hour:{hour}" = {
    "requests": 1234,
    "tokens": 56789,
    "errors": 12
}

# Uso por modelo
f"model_usage:{model}:day:{date}" = count

# Revenue tracking
f"revenue:day:{date}" = amount
```

## 🔍 Cache Manager

### LLM Response Caching
```python
import hashlib
import json
import zstandard as zstd

class LLMCacheManager:
    def __init__(self, redis_client, compression_enabled=True):
        self.redis = redis_client
        self.compression = compression_enabled
        self.compressor = zstd.ZstdCompressor() if compression_enabled else None
    
    async def get_cache_key(self, prompt: str, model: str, params: dict) -> str:
        """Generar clave única para cache"""
        cache_data = {
            "prompt": prompt,
            "model": model,
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 1000)
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"llm_cache:{hashlib.sha256(cache_string.encode()).hexdigest()}"
    
    async def get_cached_response(self, cache_key: str) -> dict:
        """Obtener respuesta desde cache"""
        try:
            cached_data = await self.redis.get(cache_key)
            if not cached_data:
                return None
            
            if self.compression:
                cached_data = self.compressor.decompress(cached_data)
            
            return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def cache_response(
        self, 
        cache_key: str, 
        response: dict, 
        ttl: int = LLM_CACHE_TTL
    ):
        """Guardar respuesta en cache"""
        try:
            data = json.dumps(response)
            
            if self.compression and len(data) > COMPRESSION_THRESHOLD:
                data = self.compressor.compress(data.encode())
            
            await self.redis.setex(cache_key, ttl, data)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
```

### Session Management
```python
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def create_session(self, user_id: str, user_data: dict) -> str:
        """Crear nueva sesión de usuario"""
        session_id = f"session:{user_id}"
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            session_id, 
            SESSION_TTL, 
            json.dumps(session_data)
        )
        return session_id
    
    async def get_session(self, user_id: str) -> dict:
        """Obtener datos de sesión"""
        session_id = f"session:{user_id}"
        session_data = await self.redis.get(session_id)
        
        if session_data:
            return json.loads(session_data)
        return None
    
    async def update_activity(self, user_id: str):
        """Actualizar última actividad"""
        session_id = f"session:{user_id}"
        session = await self.get_session(user_id)
        
        if session:
            session["last_activity"] = datetime.utcnow().isoformat()
            await self.redis.setex(
                session_id, 
                SESSION_TTL, 
                json.dumps(session)
            )
```

## 📊 Rate Limiting

### User Rate Limiting
```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        action: str,
        limit: int, 
        window: int
    ) -> dict:
        """Verificar límite de tasa para usuario"""
        
        # Usar sliding window con múltiples buckets
        now = int(time.time())
        window_start = now - window
        
        # Limpiar buckets antiguos
        pipe = self.redis.pipeline()
        for i in range(window):
            bucket_time = window_start + i
            bucket_key = f"rate:{user_id}:{action}:{bucket_time}"
            pipe.expire(bucket_key, window + 1)
        
        # Contar requests en ventana actual
        current_count = 0
        for i in range(window):
            bucket_time = window_start + i
            bucket_key = f"rate:{user_id}:{action}:{bucket_time}"
            count = await self.redis.get(bucket_key)
            if count:
                current_count += int(count)
        
        # Verificar límite
        remaining = max(0, limit - current_count)
        allowed = current_count < limit
        
        if allowed:
            # Incrementar contador actual
            current_bucket = f"rate:{user_id}:{action}:{now}"
            await self.redis.incr(current_bucket)
            await self.redis.expire(current_bucket, window + 1)
        
        return {
            "allowed": allowed,
            "current_count": current_count,
            "limit": limit,
            "remaining": remaining,
            "reset_at": window_start + window
        }
```

## 📈 Analytics Caching

### Metrics Aggregation
```python
class AnalyticsCache:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def increment_metric(
        self, 
        metric_name: str, 
        value: int = 1,
        labels: dict = None
    ):
        """Incrementar métrica agregada"""
        hour = datetime.utcnow().strftime("%Y%m%d%H")
        
        # Métrica base
        base_key = f"metrics:{metric_name}:hour:{hour}"
        await self.redis.incrby(base_key, value)
        await self.redis.expire(base_key, ANALYTICS_TTL)
        
        # Métricas con etiquetas
        if labels:
            for label_key, label_value in labels.items():
                label_key = f"metrics:{metric_name}:{label_key}:{label_value}:hour:{hour}"
                await self.redis.incrby(label_key, value)
                await self.redis.expire(label_key, ANALYTICS_TTL)
    
    async def get_metrics_range(
        self, 
        metric_name: str, 
        start_hour: str, 
        end_hour: str
    ) -> dict:
        """Obtener métricas en rango de tiempo"""
        pattern = f"metrics:{metric_name}:hour:*"
        keys = await self.redis.keys(pattern)
        
        # Filtrar por rango
        filtered_keys = [
            key for key in keys 
            if start_hour <= key.split(":")[-1] <= end_hour
        ]
        
        if not filtered_keys:
            return {}
        
        values = await self.redis.mget(filtered_keys)
        return {
            key.decode(): int(value) if value else 0 
            for key, value in zip(filtered_keys, values)
        }
```

## 🔍 Health Monitoring

### Redis Health Check
```python
class HealthMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def health_check(self) -> dict:
        """Verificar salud de Redis"""
        try:
            # Test de conectividad
            start_time = time.time()
            await self.redis.ping()
            ping_time = (time.time() - start_time) * 1000
            
            # Información del servidor
            info = await self.redis.info()
            
            # Métricas clave
            used_memory = info.get("used_memory", 0)
            max_memory = info.get("maxmemory", 0)
            memory_usage = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            # Conexiones
            connected_clients = info.get("connected_clients", 0)
            
            return {
                "status": "healthy",
                "ping_time_ms": round(ping_time, 2),
                "memory_usage_percent": round(memory_usage, 2),
                "used_memory_mb": round(used_memory / 1024 / 1024, 2),
                "connected_clients": connected_clients,
                "redis_version": info.get("redis_version", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
```

## 🧪 Testing

### Unit Tests
```bash
# Test cache operations
pytest tests/test_cache.py -v

# Test session management
pytest tests/test_sessions.py -v

# Test rate limiting
pytest tests/test_rate_limiting.py -v

# Test analytics
pytest tests/test_analytics.py -v
```

### Performance Tests
```bash
# Redis performance test
redis-benchmark -h your-redis-host -p 6379 -c 50 -n 10000

# Cache hit rate test
pytest tests/test_cache_performance.py -v
```

## 🚀 Desarrollo Local

### Setup con Redis Local
```bash
# Instalar Redis (macOS)
brew install redis

# Iniciar Redis
redis-server

# Configurar variables de entorno
export REDIS_URL=redis://localhost:6379

# Test de conexión
redis-cli ping
```

### Setup con Redis Cloud
```bash
# Configurar variables de entorno
export REDIS_URL=redis://username:password@redis-cloud-url:port
export REDIS_SSL=true

# Test de conexión
redis-cli -u $REDIS_URL ping
```

## 📊 Monitoreo y Métricas

### Métricas Clave
- Hit rate de cache LLM
- Tiempo de respuesta Redis
- Uso de memoria
- Número de conexiones activas
- Rate limiting effectiveness

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Cache metrics
cache_hits = Counter("cache_hits_total", "Cache hits", ["cache_type"])
cache_misses = Counter("cache_misses_total", "Cache misses", ["cache_type"])
cache_operation_time = Histogram("cache_operation_seconds", "Cache operation time")

# Session metrics
active_sessions = Gauge("active_sessions", "Number of active sessions")
session_duration = Histogram("session_duration_seconds", "Session duration")

# Rate limiting metrics
rate_limit_exceeded = Counter("rate_limit_exceeded_total", "Rate limit exceeded")
```

## 🔧 Optimización

### Memory Optimization
```python
# Configuraciones Redis para optimización
REDIS_CONFIG = {
    "maxmemory-policy": "allkeys-lru",
    "maxmemory-samples": 5,
    "hash-max-ziplist-entries": 512,
    "hash-max-ziplist-value": 64,
    "list-max-ziplist-size": -2,
    "set-max-intset-entries": 512,
    "zset-max-ziplist-entries": 128,
    "zset-max-ziplist-value": 64
}
```

---

**Puerto**: 6379 (Redis)  
**Estado**: 🔄 En desarrollo  
**Próximo**: Configurar Redis Cloud y conectividad 