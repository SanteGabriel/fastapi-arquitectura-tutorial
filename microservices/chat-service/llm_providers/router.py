"""
Router para seleccionar y gestionar proveedores LLM
"""

import os
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import re

# Imports locales
from .openai_provider import OpenAIProvider
# from .claude_provider import ClaudeProvider
# from .deepseek_provider import DeepSeekProvider  
# from .gemini_provider import GeminiProvider

# Imports compartidos
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models import ChatRequest
from shared.exceptions import LLMProviderException

logger = logging.getLogger(__name__)


class LLMRouter:
    """Router para gestionar múltiples proveedores LLM"""
    
    def __init__(self):
        self.providers = {}
        self.model_to_provider = {}
        self.fallback_order = ["openai", "deepseek", "gemini"]  # Claude requiere más configuración
        
    async def initialize_providers(self):
        """Inicializar todos los proveedores configurados"""
        logger.info("Initializing LLM providers...")
        
        # OpenAI
        openai_provider = OpenAIProvider()
        if await openai_provider.initialize():
            self.providers["openai"] = openai_provider
            # Mapear modelos a proveedor
            for model in openai_provider.models.keys():
                self.model_to_provider[model] = "openai"
        
        # TODO: Inicializar otros proveedores cuando estén implementados
        # claude_provider = ClaudeProvider()
        # if await claude_provider.initialize():
        #     self.providers["claude"] = claude_provider
        
        # deepseek_provider = DeepSeekProvider() 
        # if await deepseek_provider.initialize():
        #     self.providers["deepseek"] = deepseek_provider
        
        # gemini_provider = GeminiProvider()
        # if await gemini_provider.initialize():
        #     self.providers["gemini"] = gemini_provider
        
        logger.info(f"Initialized {len(self.providers)} LLM providers: {list(self.providers.keys())}")
    
    async def get_available_models(self, user_plan: str) -> List[Dict[str, Any]]:
        """Obtener modelos disponibles para el plan del usuario"""
        available_models = []
        
        # Definir modelos por plan
        plan_models = {
            "free": ["gpt-3.5-turbo"],  # Solo GPT-3.5 para usuarios free
            "premium": ["gpt-3.5-turbo", "gpt-4"],
            "enterprise": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "admin": "*"  # Todos los modelos
        }
        
        allowed_models = plan_models.get(user_plan, plan_models["free"])
        
        for provider_name, provider in self.providers.items():
            for model, info in provider.models.items():
                # Verificar si el usuario tiene acceso al modelo
                if allowed_models == "*" or model in allowed_models:
                    available_models.append({
                        "model": model,
                        "provider": provider_name,
                        "max_tokens": info["max_tokens"],
                        "supports_streaming": info["supports_streaming"],
                        "cost_per_1k_input": info["cost_per_1k_input"],
                        "cost_per_1k_output": info["cost_per_1k_output"]
                    })
        
        return available_models
    
    async def select_optimal_model(
        self, 
        message: str, 
        user_plan: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Seleccionar modelo óptimo basado en el mensaje y plan del usuario"""
        
        # Análisis del tipo de consulta
        is_code_query = self._is_code_related(message)
        is_long_message = len(message) > 2000
        is_complex_query = self._is_complex_query(message)
        
        # Selección basada en el plan y tipo de consulta
        if user_plan == "free":
            return "gpt-3.5-turbo"  # Solo opción para usuarios free
        
        elif user_plan == "premium":
            if is_complex_query or is_long_message:
                return "gpt-4"
            else:
                return "gpt-3.5-turbo"  # Más económico para consultas simples
        
        elif user_plan in ["enterprise", "admin"]:
            if is_complex_query or is_long_message:
                return "gpt-4-turbo"  # Mejor modelo para consultas complejas
            elif is_code_query:
                return "gpt-4"  # Bueno para código
            else:
                return "gpt-3.5-turbo"  # Eficiente para consultas simples
        
        # Default fallback
        return "gpt-3.5-turbo"
    
    def _is_code_related(self, message: str) -> bool:
        """Detectar si el mensaje está relacionado con código"""
        code_indicators = [
            "code", "function", "class", "import", "def ", "var ", "let ", "const ",
            "if (", "for (", "while (", "try:", "except:", "async def",
            "```", "python", "javascript", "java", "c++", "sql", "html", "css"
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in code_indicators)
    
    def _is_complex_query(self, message: str) -> bool:
        """Detectar si la consulta es compleja"""
        complexity_indicators = [
            "analyze", "explain in detail", "comprehensive", "step by step",
            "compare", "contrast", "pros and cons", "advantages and disadvantages",
            "research", "thesis", "essay", "report", "detailed analysis"
        ]
        
        message_lower = message.lower()
        word_count = len(message.split())
        
        # Consulta compleja si tiene muchas palabras o indicadores de complejidad
        return word_count > 100 or any(indicator in message_lower for indicator in complexity_indicators)
    
    async def user_has_access_to_model(self, user_plan: str, model: str) -> bool:
        """Verificar si el usuario tiene acceso a un modelo específico"""
        available_models = await self.get_available_models(user_plan)
        return any(m["model"] == model for m in available_models)
    
    async def process_chat_request(
        self, 
        request: ChatRequest, 
        model: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Procesar solicitud de chat con un modelo específico"""
        
        # Determinar qué proveedor usar
        provider_name = self.model_to_provider.get(model)
        if not provider_name:
            raise LLMProviderException(f"No provider found for model {model}")
        
        provider = self.providers.get(provider_name)
        if not provider:
            raise LLMProviderException(f"Provider {provider_name} not available")
        
        try:
            # Intentar con el proveedor principal
            return await provider.chat_completion(request, model)
            
        except Exception as e:
            logger.error(f"Primary provider {provider_name} failed: {e}")
            
            # Intentar con fallback si está habilitado
            return await self._try_fallback(request, model, user_id, [provider_name])
    
    async def _try_fallback(
        self, 
        request: ChatRequest, 
        original_model: str, 
        user_id: str,
        failed_providers: List[str]
    ) -> Dict[str, Any]:
        """Intentar con proveedores de fallback"""
        
        for fallback_provider in self.fallback_order:
            if fallback_provider in failed_providers or fallback_provider not in self.providers:
                continue
            
            provider = self.providers[fallback_provider]
            
            # Seleccionar modelo equivalente en el proveedor de fallback
            fallback_model = self._get_equivalent_model(original_model, fallback_provider)
            if not fallback_model:
                continue
            
            try:
                logger.info(f"Trying fallback: {fallback_provider}/{fallback_model}")
                result = await provider.chat_completion(request, fallback_model)
                result["fallback_used"] = True
                result["original_model"] = original_model
                return result
                
            except Exception as e:
                logger.error(f"Fallback provider {fallback_provider} also failed: {e}")
                continue
        
        raise LLMProviderException("All providers failed")
    
    def _get_equivalent_model(self, original_model: str, provider_name: str) -> Optional[str]:
        """Obtener modelo equivalente en otro proveedor"""
        if provider_name not in self.providers:
            return None
        
        provider = self.providers[provider_name]
        
        # Mapeo simple de modelos equivalentes
        equivalents = {
            "gpt-4": ["gpt-4", "claude-3-sonnet"],
            "gpt-3.5-turbo": ["gpt-3.5-turbo", "claude-3-haiku"],
            "gpt-4-turbo": ["gpt-4-turbo", "claude-3-opus"]
        }
        
        for equivalent in equivalents.get(original_model, []):
            if equivalent in provider.models:
                return equivalent
        
        # Si no hay equivalente específico, usar el primer modelo disponible
        available_models = list(provider.models.keys())
        return available_models[0] if available_models else None
    
    async def process_chat_stream(
        self, 
        request: ChatRequest, 
        model: str, 
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Procesar stream de chat"""
        
        provider_name = self.model_to_provider.get(model)
        if not provider_name:
            raise LLMProviderException(f"No provider found for model {model}")
        
        provider = self.providers.get(provider_name)
        if not provider:
            raise LLMProviderException(f"Provider {provider_name} not available")
        
        async for chunk in provider.chat_stream(request, model):
            yield chunk
    
    async def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcular costo estimado"""
        provider_name = self.model_to_provider.get(model)
        if not provider_name:
            return 0.0
        
        provider = self.providers.get(provider_name)
        if not provider:
            return 0.0
        
        return provider.calculate_cost(model, input_tokens, output_tokens)
    
    async def get_provider_status(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de un proveedor"""
        provider = self.providers.get(provider_name)
        if not provider:
            return None
        
        return await provider.health_check()
    
    async def check_all_providers_health(self) -> Dict[str, Any]:
        """Verificar salud de todos los proveedores"""
        health_status = {}
        
        for name, provider in self.providers.items():
            health_status[name] = await provider.health_check()
        
        return health_status
    
    def get_configured_providers(self) -> List[str]:
        """Obtener lista de proveedores configurados"""
        return list(self.providers.keys())
    
    async def cleanup(self):
        """Limpiar todos los proveedores"""
        for provider in self.providers.values():
            await provider.cleanup()
        
        self.providers.clear()
        self.model_to_provider.clear()
        logger.info("LLM Router cleaned up")
