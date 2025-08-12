"""
Chat Service - Servicio de Integración LLMs
Puerto: 8002
"""

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
import json
from typing import Optional

# Imports locales
from llm_providers.openai_provider import OpenAIProvider
from llm_providers.claude_provider import ClaudeProvider
from llm_providers.deepseek_provider import DeepSeekProvider
from llm_providers.gemini_provider import GeminiProvider
from llm_providers.router import LLMRouter
from utils.token_counter import TokenCounter
from utils.rate_limiter import ChatRateLimiter

# Imports compartidos
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.models import (
    SuccessResponse, ErrorResponse, HealthResponse,
    ChatRequest, ChatResponse, LLMStatus
)
from shared.auth_middleware import get_current_user
from shared.exceptions import (
    LLMProviderException, RateLimitExceededException, InsufficientPermissionsException,
    handle_service_exception
)
from shared.config import get_settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events para inicialización y limpieza"""
    # Startup
    logger.info("🚀 Starting Chat Service...")
    
    # Inicializar proveedores LLM
    await llm_router.initialize_providers()
    logger.info("✅ LLM providers initialized")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Chat Service...")
    await llm_router.cleanup()
    logger.info("✅ Chat Service stopped")


# Crear aplicación FastAPI
app = FastAPI(
    title="LLM Wrapper - Chat Service",
    description="Servicio de integración con múltiples proveedores de LLMs",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
llm_router = LLMRouter()
token_counter = TokenCounter()
rate_limiter = ChatRateLimiter()


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para excepciones"""
    if isinstance(exc, (LLMProviderException, RateLimitExceededException, 
                       InsufficientPermissionsException)):
        http_exc = handle_service_exception(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )
    
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred"
        }
    )


# Health Check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del servicio"""
    provider_health = await llm_router.check_all_providers_health()
    
    return HealthResponse(
        service="chat-service",
        status="healthy",
        version="1.0.0",
        checks={
            "providers": provider_health,
            "api_keys_configured": llm_router.get_configured_providers()
        }
    )


# Endpoints principales
@app.get("/models", response_model=SuccessResponse)
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Obtener modelos LLM disponibles para el usuario"""
    user_plan = current_user.get("role", "free")
    available_models = await llm_router.get_available_models(user_plan)
    
    return SuccessResponse(
        message="Available models retrieved successfully",
        data={
            "models": available_models,
            "user_plan": user_plan,
            "total_models": len(available_models)
        }
    )


@app.get("/models/{provider}/status", response_model=SuccessResponse)
async def get_provider_status(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener estado de un proveedor específico"""
    status_info = await llm_router.get_provider_status(provider)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PROVIDER_NOT_FOUND",
                "message": f"Provider {provider} not found"
            }
        )
    
    return SuccessResponse(
        message=f"Provider {provider} status retrieved successfully",
        data=status_info
    )


@app.post("/chat", response_model=SuccessResponse)
async def chat_completion(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Procesar solicitud de chat"""
    user_id = current_user["user_id"]
    user_plan = current_user.get("role", "free")
    
    logger.info(f"Chat request from user {user_id}: {chat_request.message[:100]}...")
    
    # Verificar rate limiting
    rate_check = await rate_limiter.check_rate_limit(user_id, user_plan)
    if not rate_check["allowed"]:
        raise RateLimitExceededException(
            f"Rate limit exceeded. Try again in {rate_check['reset_in']} seconds"
        )
    
    # Contar tokens del mensaje de entrada
    input_tokens = token_counter.count_tokens(chat_request.message)
    
    # Verificar límites de tokens diarios
    if not await rate_limiter.check_daily_token_limit(user_id, user_plan, input_tokens):
        raise RateLimitExceededException("Daily token limit exceeded")
    
    # Seleccionar modelo
    selected_model = chat_request.model or await llm_router.select_optimal_model(
        chat_request.message,
        user_plan,
        chat_request.conversation_id
    )
    
    # Verificar que el usuario tiene acceso al modelo
    if not await llm_router.user_has_access_to_model(user_plan, selected_model):
        raise InsufficientPermissionsException(
            f"Your plan does not include access to {selected_model}"
        )
    
    try:
        # Procesar chat
        start_time = time.time()
        response = await llm_router.process_chat_request(
            chat_request,
            selected_model,
            user_id
        )
        processing_time = time.time() - start_time
        
        # Contar tokens de respuesta
        output_tokens = token_counter.count_tokens(response["message"])
        total_tokens = input_tokens + output_tokens
        
        # Calcular costo estimado
        cost_estimate = await llm_router.calculate_cost(
            selected_model,
            input_tokens,
            output_tokens
        )
        
        # Actualizar contadores de rate limiting
        await rate_limiter.update_counters(user_id, total_tokens)
        
        logger.info(f"Chat completed for user {user_id}: {total_tokens} tokens, ${cost_estimate:.4f}")
        
        return SuccessResponse(
            message="Chat completed successfully",
            data={
                "message": response["message"],
                "model_used": selected_model,
                "tokens_used": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_estimate": cost_estimate,
                "conversation_id": response.get("conversation_id"),
                "processing_time": processing_time
            }
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed for user {user_id}: {e}")
        raise LLMProviderException(f"Chat processing failed: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Chat con streaming de respuesta"""
    user_id = current_user["user_id"]
    user_plan = current_user.get("role", "free")
    
    # Verificaciones similares al endpoint regular
    rate_check = await rate_limiter.check_rate_limit(user_id, user_plan)
    if not rate_check["allowed"]:
        raise RateLimitExceededException(
            f"Rate limit exceeded. Try again in {rate_check['reset_in']} seconds"
        )
    
    # Forzar streaming
    chat_request.stream = True
    
    # Seleccionar modelo
    selected_model = chat_request.model or await llm_router.select_optimal_model(
        chat_request.message,
        user_plan,
        chat_request.conversation_id
    )
    
    if not await llm_router.user_has_access_to_model(user_plan, selected_model):
        raise InsufficientPermissionsException(
            f"Your plan does not include access to {selected_model}"
        )
    
    async def generate_stream():
        """Generar stream de respuesta"""
        try:
            async for chunk in llm_router.process_chat_stream(
                chat_request,
                selected_model,
                user_id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {
                "error": True,
                "message": f"Stream processing failed: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/usage", response_model=SuccessResponse)
async def get_user_usage(current_user: dict = Depends(get_current_user)):
    """Obtener estadísticas de uso del usuario"""
    user_id = current_user["user_id"]
    user_plan = current_user.get("role", "free")
    
    usage_stats = await rate_limiter.get_user_usage_stats(user_id, user_plan)
    
    return SuccessResponse(
        message="Usage statistics retrieved successfully",
        data=usage_stats
    )


@app.post("/chat/batch", response_model=SuccessResponse)
async def batch_chat_completion(
    requests: list[ChatRequest],
    current_user: dict = Depends(get_current_user)
):
    """Procesamiento por lotes (solo para usuarios enterprise)"""
    user_plan = current_user.get("role", "free")
    
    if user_plan not in ["enterprise", "admin"]:
        raise InsufficientPermissionsException(
            "Batch processing is only available for enterprise users"
        )
    
    if len(requests) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "BATCH_TOO_LARGE",
                "message": "Maximum 100 requests per batch"
            }
        )
    
    results = []
    for i, chat_request in enumerate(requests):
        try:
            # Procesar cada request individualmente
            response = await llm_router.process_chat_request(
                chat_request,
                chat_request.model or "gpt-3.5-turbo",
                current_user["user_id"]
            )
            results.append({
                "index": i,
                "success": True,
                "data": response
            })
        except Exception as e:
            results.append({
                "index": i,
                "success": False,
                "error": str(e)
            })
    
    return SuccessResponse(
        message=f"Batch processing completed: {len([r for r in results if r['success']])} successful",
        data={
            "results": results,
            "total_requests": len(requests),
            "successful_requests": len([r for r in results if r['success']]),
            "failed_requests": len([r for r in results if not r['success']])
        }
    )


# Helper imports
import time


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
