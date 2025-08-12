"""
Modelos y repositorio de usuario para Auth Service
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.database import BaseRepository, get_database_manager
from shared.exceptions import UserNotFoundException


class UserRepository(BaseRepository):
    """Repositorio para operaciones de usuario"""
    
    def __init__(self):
        super().__init__("users")
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crear nuevo usuario"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user_document = {
            "id": user_id,
            "name": user_data["name"],
            "email": user_data["email"].lower(),
            "password_hash": user_data["password_hash"],
            "subscription_status": user_data.get("subscription_status", "free"),
            "subscription_expires": user_data.get("subscription_expires"),
            "is_active": user_data.get("is_active", True),
            "email_verified": user_data.get("email_verified", False),
            "last_login": None,
            "created_at": now,
            "updated_at": now
        }
        
        collection = self.get_collection()
        await collection.insert_one(user_document)
        return user_id
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Buscar usuario por email"""
        collection = self.get_collection()
        user = await collection.find_one({"email": email.lower()})
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Buscar usuario por ID"""
        collection = self.get_collection()
        user = await collection.find_one({"id": user_id})
        return user
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Actualizar datos de usuario"""
        collection = self.get_collection()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def update_last_login(self, user_id: str) -> bool:
        """Actualizar timestamp de último login"""
        return await self.update_user(user_id, {"last_login": datetime.utcnow()})
    
    async def update_subscription(
        self, 
        user_id: str, 
        subscription_status: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Actualizar estado de suscripción"""
        update_data = {
            "subscription_status": subscription_status,
            "subscription_expires": expires_at
        }
        return await self.update_user(user_id, update_data)
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Desactivar usuario"""
        return await self.update_user(user_id, {"is_active": False})
    
    async def activate_user(self, user_id: str) -> bool:
        """Activar usuario"""
        return await self.update_user(user_id, {"is_active": True})
    
    async def verify_email(self, user_id: str) -> bool:
        """Marcar email como verificado"""
        return await self.update_user(user_id, {"email_verified": True})
    
    async def change_password(self, user_id: str, new_password_hash: str) -> bool:
        """Cambiar contraseña del usuario"""
        return await self.update_user(user_id, {"password_hash": new_password_hash})
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas básicas del usuario"""
        user = await self.get_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        # Calcular días desde registro
        created_at = user.get("created_at")
        days_registered = 0
        if created_at:
            days_registered = (datetime.utcnow() - created_at).days
        
        return {
            "user_id": user_id,
            "days_registered": days_registered,
            "subscription_status": user.get("subscription_status", "free"),
            "email_verified": user.get("email_verified", False),
            "last_login": user.get("last_login"),
            "is_active": user.get("is_active", True)
        }
    
    async def search_users(
        self, 
        query: str = None,
        subscription_status: str = None,
        is_active: bool = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Buscar usuarios con filtros (para admin)"""
        collection = self.get_collection()
        
        # Construir filtro
        filter_dict = {}
        
        if query:
            filter_dict["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        
        if subscription_status:
            filter_dict["subscription_status"] = subscription_status
            
        if is_active is not None:
            filter_dict["is_active"] = is_active
        
        # Contar total
        total_count = await collection.count_documents(filter_dict)
        
        # Obtener usuarios
        cursor = collection.find(
            filter_dict,
            {"password_hash": 0}  # Excluir hash de contraseña
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        users = await cursor.to_list(length=limit)
        
        return {
            "users": users,
            "total_count": total_count,
            "page": (skip // limit) + 1,
            "page_size": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
