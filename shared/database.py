"""
Utilidades para base de datos MongoDB
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from .exceptions import DatabaseConnectionException
from .config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manager para conexiones de base de datos MongoDB"""
    
    def __init__(self, mongodb_uri: str, database_name: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            
            # Test de conectividad
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {self.database_name}")
            
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseConnectionException(f"Failed to connect to MongoDB: {e}")
    
    async def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud de la base de datos"""
        try:
            result = await self.client.admin.command('ping')
            server_info = await self.client.server_info()
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "mongodb_version": server_info.get("version"),
                "ping_result": result
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_collection(self, collection_name: str):
        """Obtener una colección"""
        if not self.db:
            raise DatabaseConnectionException("Database not connected")
        return self.db[collection_name]


# Singleton global para manejo de base de datos
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """Obtener instancia singleton del database manager"""
    global _db_manager
    if _db_manager is None:
        settings = get_settings()
        _db_manager = DatabaseManager(
            settings.MONGODB_URI,
            "llm_wrapper"  # Base de datos principal
        )
    return _db_manager


@asynccontextmanager
async def get_database():
    """Context manager para obtener conexión a base de datos"""
    db_manager = get_database_manager()
    if not db_manager.db:
        await db_manager.connect()
    yield db_manager.db


async def create_indexes(db: AsyncIOMotorDatabase):
    """Crear índices optimizados para la base de datos"""
    try:
        # Índices para usuarios
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        await db.users.create_index([("email", 1), ("is_active", 1)])
        
        # Índices para conversaciones
        await db.conversations.create_index([("user_id", 1), ("created_at", -1)])
        await db.conversations.create_index([("user_id", 1), ("is_favorite", 1)])
        await db.conversations.create_index([("user_id", 1), ("tags", 1)])
        await db.conversations.create_index("retention_until")
        
        # Índice de texto completo para búsqueda
        await db.conversations.create_index([
            ("title", "text"),
            ("tags", "text")
        ])
        
        # Índices para mensajes
        await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
        await db.messages.create_index([("conversation_id", 1), ("role", 1)])
        
        # Índices para suscripciones
        await db.subscriptions.create_index("user_id", unique=True)
        await db.subscriptions.create_index([("status", 1), ("current_period_end", 1)])
        
        # Índices para transacciones
        await db.transactions.create_index([("user_id", 1), ("created_at", -1)])
        await db.transactions.create_index("provider_transaction_id", unique=True)
        await db.transactions.create_index([("status", 1), ("created_at", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")


# Helper functions para operaciones comunes
class BaseRepository:
    """Clase base para repositorios de datos"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db_manager = get_database_manager()
    
    def get_collection(self):
        """Obtener la colección"""
        return self.db_manager.get_collection(self.collection_name)
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Buscar documento por ID"""
        collection = self.get_collection()
        return await collection.find_one({"id": id})
    
    async def create(self, data: Dict[str, Any]) -> str:
        """Crear nuevo documento"""
        collection = self.get_collection()
        result = await collection.insert_one(data)
        return data.get("id")
    
    async def update_by_id(self, id: str, data: Dict[str, Any]) -> bool:
        """Actualizar documento por ID"""
        collection = self.get_collection()
        # Agregar timestamp de actualización
        data["updated_at"] = datetime.utcnow()
        result = await collection.update_one({"id": id}, {"$set": data})
        return result.modified_count > 0
    
    async def delete_by_id(self, id: str) -> bool:
        """Eliminar documento por ID"""
        collection = self.get_collection()
        result = await collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def find_many(
        self, 
        filter_dict: Dict[str, Any] = None, 
        skip: int = 0, 
        limit: int = 100,
        sort: Dict[str, int] = None
    ) -> list:
        """Buscar múltiples documentos con paginación"""
        collection = self.get_collection()
        cursor = collection.find(filter_dict or {})
        
        if sort:
            cursor = cursor.sort(list(sort.items()))
        
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Contar documentos que coinciden con el filtro"""
        collection = self.get_collection()
        return await collection.count_documents(filter_dict or {})


# Inicialización de la base de datos para aplicaciones FastAPI
async def init_database():
    """Inicializar conexión a base de datos"""
    db_manager = get_database_manager()
    await db_manager.connect()
    await create_indexes(db_manager.db)


async def close_database():
    """Cerrar conexión a base de datos"""
    db_manager = get_database_manager()
    await db_manager.disconnect()
