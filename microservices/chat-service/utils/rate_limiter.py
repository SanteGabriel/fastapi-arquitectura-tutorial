"""
Rate Limiter simple para Chat Service
"""

import time
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Imports compartidos
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.config import SubscriptionPlans


class ChatRateLimiter:
    """Rate Limiter simple en memoria para Chat Service"""
    
    def __init__(self):
        # Almacenamiento en memoria (en producción usar Redis)
        self.user_requests = defaultdict(deque)  # user_id -> deque of timestamps
        self.user_tokens = defaultdict(dict)     # user_id -> {date: token_count}
        
        # Límites por plan
        self.rate_limits = {
            "free": {
                "requests_per_hour": 50,
                "tokens_per_day": 10000
            },
            "premium": {
                "requests_per_hour": 500,
                "tokens_per_day": 100000
            },
            "enterprise": {
                "requests_per_hour": 5000,
                "tokens_per_day": 1000000
            },
            "admin": {
                "requests_per_hour": 10000,
                "tokens_per_day": 2000000
            }
        }
    
    async def check_rate_limit(self, user_id: str, user_plan: str) -> Dict[str, Any]:
        """Verificar límite de requests por hora"""
        now = time.time()
        hour_ago = now - 3600  # 1 hora atrás
        
        # Limpiar requests antiguos
        user_deque = self.user_requests[user_id]
        while user_deque and user_deque[0] < hour_ago:
            user_deque.popleft()
        
        # Verificar límite
        plan_limits = self.rate_limits.get(user_plan, self.rate_limits["free"])
        limit = plan_limits["requests_per_hour"]
        current_count = len(user_deque)
        
        if current_count >= limit:
            # Calcular tiempo hasta reset
            oldest_request = user_deque[0] if user_deque else now
            reset_in = int(oldest_request + 3600 - now)
            
            return {
                "allowed": False,
                "current_count": current_count,
                "limit": limit,
                "reset_in": max(reset_in, 0)
            }
        
        # Agregar request actual
        user_deque.append(now)
        
        return {
            "allowed": True,
            "current_count": current_count + 1,
            "limit": limit,
            "reset_in": 3600
        }
    
    async def check_daily_token_limit(
        self, 
        user_id: str, 
        user_plan: str, 
        tokens_to_use: int
    ) -> bool:
        """Verificar límite de tokens diarios"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Obtener uso actual del día
        user_token_data = self.user_tokens[user_id]
        current_tokens = user_token_data.get(today, 0)
        
        # Verificar límite
        plan_limits = self.rate_limits.get(user_plan, self.rate_limits["free"])
        daily_limit = plan_limits["tokens_per_day"]
        
        return (current_tokens + tokens_to_use) <= daily_limit
    
    async def update_counters(self, user_id: str, tokens_used: int):
        """Actualizar contadores de uso"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Actualizar tokens diarios
        user_token_data = self.user_tokens[user_id]
        user_token_data[today] = user_token_data.get(today, 0) + tokens_used
        
        # Limpiar datos antiguos (mantener solo últimos 7 días)
        cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        keys_to_remove = [
            date for date in user_token_data.keys() 
            if date < cutoff_date
        ]
        for key in keys_to_remove:
            del user_token_data[key]
    
    async def get_user_usage_stats(self, user_id: str, user_plan: str) -> Dict[str, Any]:
        """Obtener estadísticas de uso del usuario"""
        today = datetime.now().strftime("%Y-%m-%d")
        now = time.time()
        hour_ago = now - 3600
        
        # Requests en la última hora
        user_deque = self.user_requests[user_id]
        recent_requests = sum(1 for timestamp in user_deque if timestamp > hour_ago)
        
        # Tokens usados hoy
        user_token_data = self.user_tokens[user_id]
        tokens_today = user_token_data.get(today, 0)
        
        # Límites del plan
        plan_limits = self.rate_limits.get(user_plan, self.rate_limits["free"])
        
        return {
            "user_plan": user_plan,
            "usage": {
                "requests_last_hour": recent_requests,
                "tokens_today": tokens_today,
                "requests_limit_hour": plan_limits["requests_per_hour"],
                "tokens_limit_day": plan_limits["tokens_per_day"]
            },
            "remaining": {
                "requests_hour": max(0, plan_limits["requests_per_hour"] - recent_requests),
                "tokens_day": max(0, plan_limits["tokens_per_day"] - tokens_today)
            },
            "percentage_used": {
                "requests": (recent_requests / plan_limits["requests_per_hour"]) * 100,
                "tokens": (tokens_today / plan_limits["tokens_per_day"]) * 100
            }
        }
    
    def get_plan_limits(self, user_plan: str) -> Dict[str, int]:
        """Obtener límites del plan"""
        return self.rate_limits.get(user_plan, self.rate_limits["free"])
    
    async def reset_user_limits(self, user_id: str):
        """Resetear límites de un usuario (para testing o admin)"""
        if user_id in self.user_requests:
            self.user_requests[user_id].clear()
        
        if user_id in self.user_tokens:
            self.user_tokens[user_id].clear()
    
    def get_all_user_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas globales (para admin)"""
        total_users = len(set(list(self.user_requests.keys()) + list(self.user_tokens.keys())))
        
        # Requests en la última hora por todos los usuarios
        now = time.time()
        hour_ago = now - 3600
        total_requests_hour = sum(
            sum(1 for timestamp in deque_data if timestamp > hour_ago)
            for deque_data in self.user_requests.values()
        )
        
        # Tokens usados hoy por todos los usuarios
        today = datetime.now().strftime("%Y-%m-%d")
        total_tokens_today = sum(
            token_data.get(today, 0)
            for token_data in self.user_tokens.values()
        )
        
        return {
            "total_active_users": total_users,
            "total_requests_last_hour": total_requests_hour,
            "total_tokens_today": total_tokens_today,
            "average_requests_per_user": total_requests_hour / max(total_users, 1),
            "average_tokens_per_user": total_tokens_today / max(total_users, 1)
        }
