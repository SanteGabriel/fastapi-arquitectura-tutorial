"""
OpenAI Provider para Chat Service
"""

import openai
import os
import logging
from typing import Dict, Any, AsyncGenerator, Optional
import time

# Imports compartidos
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models import ChatRequest
from shared.exceptions import LLMProviderException

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """Proveedor para APIs de OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.name = "openai"
        self.models = {
            "gpt-4": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03,
                "supports_streaming": True
            },
            "gpt-4-turbo": {
                "max_tokens": 128000,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03,
                "supports_streaming": True
            },
            "gpt-3.5-turbo": {
                "max_tokens": 16385,
                "cost_per_1k_input": 0.0015,
                "cost_per_1k_output": 0.002,
                "supports_streaming": True
            }
        }
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar el proveedor"""
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return False
        
        try:
            # Configurar cliente OpenAI
            openai.api_key = self.api_key
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Test de conectividad
            await self._test_connection()
            self.is_initialized = True
            logger.info("✅ OpenAI provider initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI provider: {e}")
            return False
    
    async def _test_connection(self):
        """Probar conexión con OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            raise LLMProviderException(f"OpenAI connection test failed: {e}")
    
    async def chat_completion(
        self,
        request: ChatRequest,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """Completión de chat estándar"""
        if not self.is_initialized:
            raise LLMProviderException("OpenAI provider not initialized")
        
        if model not in self.models:
            raise LLMProviderException(f"Model {model} not supported by OpenAI")
        
        try:
            # Preparar mensajes
            messages = []
            
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            messages.append({"role": "user", "content": request.message})
            
            # Configurar parámetros
            params = {
                "model": model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or 1000,
                "stream": False
            }
            
            start_time = time.time()
            response = await self.client.chat.completions.create(**params)
            processing_time = time.time() - start_time
            
            result = {
                "message": response.choices[0].message.content,
                "model": model,
                "provider": self.name,
                "tokens_used": response.usage.total_tokens,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "processing_time": processing_time
            }
            
            logger.info(f"OpenAI completion: {result['tokens_used']} tokens, {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise LLMProviderException(f"OpenAI completion failed: {str(e)}")
    
    async def chat_stream(
        self,
        request: ChatRequest,
        model: str = "gpt-3.5-turbo"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream de chat"""
        if not self.is_initialized:
            raise LLMProviderException("OpenAI provider not initialized")
        
        if model not in self.models:
            raise LLMProviderException(f"Model {model} not supported by OpenAI")
        
        try:
            # Preparar mensajes
            messages = []
            
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            
            messages.append({"role": "user", "content": request.message})
            
            # Configurar parámetros para streaming
            params = {
                "model": model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or 1000,
                "stream": True
            }
            
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "delta": chunk.choices[0].delta.content,
                        "model": model,
                        "provider": self.name,
                        "done": False
                    }
            
            # Chunk final
            yield {
                "delta": "",
                "model": model,
                "provider": self.name,
                "done": True
            }
            
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise LLMProviderException(f"OpenAI streaming failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud del proveedor"""
        if not self.api_key:
            return {
                "status": "error",
                "message": "API key not configured"
            }
        
        if not self.is_initialized:
            return {
                "status": "error", 
                "message": "Provider not initialized"
            }
        
        try:
            start_time = time.time()
            await self._test_connection()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "models": list(self.models.keys()),
                "supports_streaming": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un modelo"""
        return self.models.get(model)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcular costo estimado"""
        model_info = self.models.get(model)
        if not model_info:
            return 0.0
        
        input_cost = (input_tokens / 1000) * model_info["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * model_info["cost_per_1k_output"]
        
        return input_cost + output_cost
    
    async def cleanup(self):
        """Limpiar recursos"""
        if self.client:
            await self.client.close()
        self.is_initialized = False
        logger.info("OpenAI provider cleaned up")
