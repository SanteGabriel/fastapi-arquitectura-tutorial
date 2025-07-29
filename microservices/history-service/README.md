# 📚 History Service - Servicio de Historial

## 📋 Descripción
Microservicio responsable de la gestión del historial de conversaciones, almacenamiento en MongoDB Atlas y funcionalidades de búsqueda para el sistema LLM Wrapper Web.

## 🏗️ Arquitectura del Servicio

```
┌─────────────────────────────────────────┐
│            HISTORY SERVICE              │
│              Puerto: 8004               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Routes    │    │  Middleware │    │
│  │             │    │             │    │
│  │ /save       │◄──►│ Auth Check  │    │
│  │ /search     │    │ Validation  │    │
│  │ /export     │    │ Rate Limit  │    │
│  │ /delete     │    │ Pagination  │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │Conversation │    │   Search    │    │
│  │  Manager    │    │   Engine    │    │
│  │             │    │             │    │
│  │ CRUD Ops    │    │ Full Text   │    │
│  │ Validation  │    │ Filters     │    │
│  │ Indexing    │    │ Sorting     │    │
│  │ Compression │    │ Facets      │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  Export     │    │   Utils     │    │
│  │  Engine     │    │             │    │
│  │             │    │ Date Utils  │    │
│  │ PDF Export  │    │ Formatters  │    │
│  │ JSON Export │    │ Validators  │    │
│  │ TXT Export  │    │ Sanitizers  │    │
│  └─────────────┘    └─────────────┘    │
│         │                              │
│         ▼                              │
│  ┌─────────────────────────────────┐   │
│  │         DATABASE                │   │
│  │      MongoDB Atlas              │   │
│  │                                 │   │
│  │ Collections:                    │   │
│  │ - conversations                 │   │
│  │ - messages                      │   │
│  │ - exports                       │   │
│  │ - user_preferences             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Funcionalidades

### Core Features
- **Almacenamiento Persistente**: Conversaciones en MongoDB Atlas
- **Búsqueda Avanzada**: Full-text search con filtros
- **Exportación Múltiple**: PDF, JSON, TXT formats
- **Organización**: Categorías, etiquetas y favoritos
- **Retención Inteligente**: Políticas por plan de suscripción
- **Compresión**: Optimización de almacenamiento

### Endpoints Principales

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| POST | `/conversations` | Crear nueva conversación | ✅ |
| GET | `/conversations` | Listar conversaciones | ✅ |
| GET | `/conversations/{id}` | Obtener conversación específica | ✅ |
| PUT | `/conversations/{id}` | Actualizar conversación | ✅ |
| DELETE | `/conversations/{id}` | Eliminar conversación | ✅ |
| GET | `/search` | Buscar en historial | ✅ |
| POST | `/export` | Exportar conversaciones | ✅ |
| GET | `/stats` | Estadísticas de uso | ✅ |

## 📊 Modelos de Datos

### Conversation Model
```python
class Conversation(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    message_count: int
    total_tokens: int
    models_used: List[str]
    tags: List[str]
    category: Optional[str]
    is_favorite: bool = False
    is_archived: bool = False
    retention_until: Optional[datetime]
    metadata: Dict[str, Any]
```

### Message Model
```python
class Message(BaseModel):
    id: str
    conversation_id: str
    role: str  # user, assistant, system
    content: str
    model_used: Optional[str]
    tokens_used: int
    cost_estimate: float
    timestamp: datetime
    processing_time: Optional[float]
    metadata: Dict[str, Any]
    parent_message_id: Optional[str]  # Para conversaciones ramificadas
```

### Export Model
```python
class Export(BaseModel):
    id: str
    user_id: str
    export_type: str  # pdf, json, txt
    conversation_ids: List[str]
    filters: Dict[str, Any]
    status: str  # pending, completed, failed
    file_path: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    expires_at: datetime
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_history
CONVERSATIONS_COLLECTION=conversations
MESSAGES_COLLECTION=messages
EXPORTS_COLLECTION=exports
USER_PREFERENCES_COLLECTION=user_preferences

# Search Configuration
ENABLE_FULL_TEXT_SEARCH=true
SEARCH_INDEX_NAME=conversation_search
MAX_SEARCH_RESULTS=100
SEARCH_TIMEOUT_SECONDS=10

# Retention Policies (days)
FREE_RETENTION_DAYS=30
PREMIUM_RETENTION_DAYS=365
ENTERPRISE_RETENTION_DAYS=0  # 0 = unlimited

# Export Configuration
EXPORT_MAX_FILE_SIZE_MB=100
EXPORT_TTL_HOURS=24
EXPORT_STORAGE_PATH=/tmp/exports
ENABLE_EXPORT_COMPRESSION=true

# Performance
ENABLE_COMPRESSION=true
COMPRESSION_THRESHOLD_KB=1
ENABLE_PAGINATION=true
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Dependencias (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pymongo==4.6.0
motor==3.3.2
reportlab==4.0.7
fpdf2==2.7.6
python-multipart==0.0.6
aiofiles==23.2.1
python-dateutil==2.8.2
elasticsearch==8.11.1
redis==5.0.1
celery==5.3.4
```

## 🔍 Sistema de Búsqueda

### Full-Text Search
```python
async def search_conversations(
    user_id: str,
    query: str,
    filters: Dict[str, Any] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    Búsqueda avanzada en conversaciones con:
    - Full-text search en contenido de mensajes
    - Filtros por fecha, modelo, categoría
    - Ordenamiento por relevancia/fecha
    - Paginación optimizada
    """
    
    search_pipeline = [
        # Text search stage
        {
            "$search": {
                "index": "conversation_search",
                "text": {
                    "query": query,
                    "path": ["title", "messages.content"]
                }
            }
        },
        
        # Apply filters
        {"$match": build_search_filters(user_id, filters)},
        
        # Add score for ranking
        {"$addFields": {"relevance_score": {"$meta": "searchScore"}}},
        
        # Sort by relevance and date
        {"$sort": {"relevance_score": -1, "updated_at": -1}},
        
        # Pagination
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size}
    ]
    
    results = await db.conversations.aggregate(search_pipeline).to_list(None)
    return format_search_results(results, query)
```

### Search Filters
```python
AVAILABLE_FILTERS = {
    "date_range": {"start_date": datetime, "end_date": datetime},
    "models": ["openai", "claude", "deepseek", "gemini"],
    "categories": ["work", "personal", "research", "coding"],
    "tags": List[str],
    "is_favorite": bool,
    "message_count_range": {"min": int, "max": int},
    "token_count_range": {"min": int, "max": int}
}
```

## 📤 Sistema de Exportación

### PDF Export
```python
async def export_to_pdf(
    user_id: str,
    conversation_ids: List[str],
    include_metadata: bool = True
) -> str:
    """Exportar conversaciones a PDF con formato profesional"""
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    # Crear documento PDF
    pdf_path = f"/tmp/exports/{user_id}_{timestamp()}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    
    story = []
    styles = getSampleStyleSheet()
    
    for conv_id in conversation_ids:
        conversation = await get_conversation(conv_id, user_id)
        
        # Título de conversación
        story.append(Paragraph(conversation.title, styles['Title']))
        story.append(Spacer(1, 12))
        
        # Metadatos si se solicitan
        if include_metadata:
            metadata_text = format_conversation_metadata(conversation)
            story.append(Paragraph(metadata_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Mensajes
        messages = await get_conversation_messages(conv_id)
        for msg in messages:
            role_style = styles['Heading2'] if msg.role == 'user' else styles['Normal']
            story.append(Paragraph(f"{msg.role.title()}: {msg.content}", role_style))
            story.append(Spacer(1, 8))
    
    doc.build(story)
    return pdf_path
```

### JSON Export
```python
async def export_to_json(
    user_id: str,
    conversation_ids: List[str],
    include_metadata: bool = True
) -> str:
    """Exportar conversaciones a JSON estructurado"""
    
    export_data = {
        "export_info": {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "total_conversations": len(conversation_ids),
            "format_version": "1.0"
        },
        "conversations": []
    }
    
    for conv_id in conversation_ids:
        conversation = await get_conversation_with_messages(conv_id, user_id)
        
        conv_data = {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "message_count": conversation.message_count,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "model_used": msg.model_used,
                    "tokens_used": msg.tokens_used
                }
                for msg in conversation.messages
            ]
        }
        
        if include_metadata:
            conv_data["metadata"] = conversation.metadata
        
        export_data["conversations"].append(conv_data)
    
    json_path = f"/tmp/exports/{user_id}_{timestamp()}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return json_path
```

## 🗄️ Políticas de Retención

### Automatic Cleanup
```python
async def apply_retention_policies():
    """Aplicar políticas de retención automáticamente"""
    
    # Obtener configuraciones por plan
    retention_configs = {
        "free": timedelta(days=FREE_RETENTION_DAYS),
        "premium": timedelta(days=PREMIUM_RETENTION_DAYS),
        "enterprise": None  # Sin límite
    }
    
    for plan, retention_period in retention_configs.items():
        if retention_period is None:
            continue
        
        cutoff_date = datetime.utcnow() - retention_period
        
        # Marcar conversaciones para eliminación
        await db.conversations.update_many(
            {
                "user_subscription": plan,
                "created_at": {"$lt": cutoff_date},
                "is_archived": False
            },
            {
                "$set": {
                    "retention_until": datetime.utcnow() + timedelta(days=7),
                    "is_archived": True
                }
            }
        )
    
    # Eliminar conversaciones que han pasado el período de gracia
    await db.conversations.delete_many({
        "retention_until": {"$lt": datetime.utcnow()}
    })
```

## 📊 Analytics y Estadísticas

### User Statistics
```python
async def get_user_statistics(user_id: str) -> Dict[str, Any]:
    """Obtener estadísticas de uso del usuario"""
    
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_conversations": {"$sum": 1},
                "total_messages": {"$sum": "$message_count"},
                "total_tokens": {"$sum": "$total_tokens"},
                "models_used": {"$addToSet": "$models_used"},
                "avg_messages_per_conversation": {"$avg": "$message_count"},
                "first_conversation": {"$min": "$created_at"},
                "last_conversation": {"$max": "$updated_at"}
            }
        }
    ]
    
    stats = await db.conversations.aggregate(pipeline).to_list(1)
    
    if not stats:
        return get_empty_statistics()
    
    # Agregar estadísticas adicionales
    stats[0].update({
        "conversations_this_month": await count_conversations_this_month(user_id),
        "most_used_model": await get_most_used_model(user_id),
        "avg_tokens_per_message": stats[0]["total_tokens"] / max(stats[0]["total_messages"], 1)
    })
    
    return stats[0]
```

## 🧪 Testing

### Unit Tests
```bash
# Test CRUD operations
pytest tests/test_conversations.py -v

# Test search functionality
pytest tests/test_search.py -v

# Test export features
pytest tests/test_exports.py -v

# Test retention policies
pytest tests/test_retention.py -v
```

### Performance Tests
```bash
# Test search performance with large datasets
pytest tests/test_search_performance.py -v

# Test pagination performance
pytest tests/test_pagination.py -v

# Load test with concurrent users
locust -f tests/load_test.py --host=http://localhost:8004
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
# Editar .env con tu MongoDB URI

# Crear índices de MongoDB
python scripts/create_indexes.py

# Ejecutar servicio
uvicorn main:app --reload --port 8004
```

### MongoDB Indexes
```javascript
// Crear índices para búsqueda y rendimiento
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
db.conversations.createIndex({ "user_id": 1, "is_favorite": 1 })
db.conversations.createIndex({ "user_id": 1, "tags": 1 })
db.conversations.createIndex({ "retention_until": 1 })

// Índice de texto completo para búsqueda
db.conversations.createIndex({
  "title": "text",
  "tags": "text"
})

// Índices para mensajes
db.messages.createIndex({ "conversation_id": 1, "timestamp": 1 })
db.messages.createIndex({ "conversation_id": 1, "role": 1 })
```

## 📈 Monitoreo y Métricas

### Métricas Clave
- Número de conversaciones por usuario
- Tiempo de respuesta de búsquedas
- Tamaño promedio de conversaciones
- Uso de funciones de exportación
- Efectividad de políticas de retención

### Performance Monitoring
```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de conversaciones
conversations_created = Counter("conversations_created_total", "Total conversations created")
conversations_deleted = Counter("conversations_deleted_total", "Total conversations deleted")
search_requests = Counter("search_requests_total", "Total search requests")
search_duration = Histogram("search_duration_seconds", "Search request duration")
export_requests = Counter("export_requests_total", "Total export requests", ["format"])

# Métricas de almacenamiento
total_conversations = Gauge("total_conversations", "Total conversations in database")
total_messages = Gauge("total_messages", "Total messages in database")
database_size = Gauge("database_size_bytes", "Database size in bytes")
```

---

**Puerto**: 8004  
**Estado**: 🔄 En desarrollo  
**Próximo**: Implementar conexión MongoDB y CRUD básico 