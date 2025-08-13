#!/bin/bash

# =================================================
# SMART ENV SETUP SCRIPT - LLM WRAPPER PROJECT
# =================================================
# Este script distribuye SOLO las variables necesarias a cada servicio

set -e

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    SMART ENV SETUP SCRIPT v2.0        ${NC}"
echo -e "${BLUE}========================================${NC}"

# Verificar que existe el archivo .env global
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo .env en el directorio raíz${NC}"
    echo -e "${YELLOW}💡 Solución rápida:${NC}"
    echo -e "   cp .env.example .env && nano .env"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env global encontrado${NC}"

# Función para extraer variables específicas
extract_vars() {
    local source_file=$1
    local target_file=$2
    shift 2
    local vars=("$@")
    
    echo "# Auto-generated from global .env" > "$target_file"
    echo "# Only includes variables needed for this service" >> "$target_file"
    echo "" >> "$target_file"
    
    for var in "${vars[@]}"; do
        grep "^${var}=" "$source_file" >> "$target_file" 2>/dev/null || true
    done
}

# Variables por servicio (solo las necesarias)
AUTH_VARS=(
    "JWT_SECRET_KEY"
    "JWT_ALGORITHM" 
    "MONGODB_URI"
    "MONGODB_AUTH_DB"
    "ENVIRONMENT"
    "LOG_LEVEL"
    "CORS_ORIGINS"
)

CHAT_VARS=(
    "OPENAI_API_KEY"
    "CLAUDE_API_KEY"
    "DEEPSEEK_API_KEY"
    "GEMINI_API_KEY"
    "ENVIRONMENT"
    "LOG_LEVEL"
    "CORS_ORIGINS"
)

HISTORY_VARS=(
    "MONGODB_URI"
    "MONGODB_HISTORY_DB"
    "ENVIRONMENT"
    "LOG_LEVEL"
)

PAYMENT_VARS=(
    "STRIPE_SECRET_KEY"
    "STRIPE_PUBLISHABLE_KEY" 
    "STRIPE_WEBHOOK_SECRET"
    "MERCADOPAGO_ACCESS_TOKEN"
    "MERCADOPAGO_PUBLIC_KEY"
    "MONGODB_URI"
    "MONGODB_PAYMENTS_DB"
    "ENVIRONMENT"
)

CACHE_VARS=(
    "REDIS_URL"
    "REDIS_PASSWORD"
    "ENVIRONMENT"
    "LOG_LEVEL"
)

FRONTEND_VARS=(
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_AUTH_SERVICE_URL"
    "NEXT_PUBLIC_CHAT_SERVICE_URL"
    "STRIPE_PUBLISHABLE_KEY"
    "MERCADOPAGO_PUBLIC_KEY"
)

# Crear .env optimizado para cada servicio
echo -e "\n${BLUE}🔧 Configurando microservicios (smart mode)...${NC}"

mkdir -p microservices/auth-service
extract_vars ".env" "microservices/auth-service/.env" "${AUTH_VARS[@]}"
echo -e "${GREEN}   ✅ Auth Service - ${#AUTH_VARS[@]} variables${NC}"

mkdir -p microservices/chat-service  
extract_vars ".env" "microservices/chat-service/.env" "${CHAT_VARS[@]}"
echo -e "${GREEN}   ✅ Chat Service - ${#CHAT_VARS[@]} variables${NC}"

mkdir -p microservices/history-service
extract_vars ".env" "microservices/history-service/.env" "${HISTORY_VARS[@]}"
echo -e "${GREEN}   ✅ History Service - ${#HISTORY_VARS[@]} variables${NC}"

mkdir -p microservices/payment-service
extract_vars ".env" "microservices/payment-service/.env" "${PAYMENT_VARS[@]}"
echo -e "${GREEN}   ✅ Payment Service - ${#PAYMENT_VARS[@]} variables${NC}"

mkdir -p microservices/cache-service
extract_vars ".env" "microservices/cache-service/.env" "${CACHE_VARS[@]}"
echo -e "${GREEN}   ✅ Cache Service - ${#CACHE_VARS[@]} variables${NC}"

# Frontend (Next.js)
if [ -d "frontend" ]; then
    mkdir -p frontend
    echo "# Next.js Environment Variables" > "frontend/.env.local"
    echo "# Only public variables for client-side" >> "frontend/.env.local"
    echo "" >> "frontend/.env.local"
    
    # Agregar URLs de API (hardcoded para desarrollo)
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" >> "frontend/.env.local"
    echo "NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8001" >> "frontend/.env.local"
    echo "NEXT_PUBLIC_CHAT_SERVICE_URL=http://localhost:8002" >> "frontend/.env.local"
    echo "" >> "frontend/.env.local"
    
    # Solo claves públicas de pagos
    grep "STRIPE_PUBLISHABLE_KEY" .env >> "frontend/.env.local" 2>/dev/null || true
    grep "MERCADOPAGO_PUBLIC_KEY" .env >> "frontend/.env.local" 2>/dev/null || true
    
    echo -e "${GREEN}   ✅ Frontend - Solo variables públicas${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}    ✅ CONFIGURACIÓN INTELIGENTE OK     ${NC}" 
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}📊 Estadísticas:${NC}"
echo -e "   🔐 Auth Service: ${#AUTH_VARS[@]} variables (JWT + MongoDB)"
echo -e "   🤖 Chat Service: ${#CHAT_VARS[@]} variables (LLM APIs)"
echo -e "   📚 History Service: ${#HISTORY_VARS[@]} variables (MongoDB)"
echo -e "   💳 Payment Service: ${#PAYMENT_VARS[@]} variables (Stripe + MP)"
echo -e "   ⚡ Cache Service: ${#CACHE_VARS[@]} variables (Redis)"
echo -e "   🎨 Frontend: Solo variables públicas"

echo -e "\n${YELLOW}🔍 Variables obligatorias detectadas:${NC}"
grep -q "^JWT_SECRET_KEY=" .env && echo -e "   ✅ JWT_SECRET_KEY" || echo -e "   ❌ JWT_SECRET_KEY (OBLIGATORIA)"
grep -q "^MONGODB_URI=" .env && echo -e "   ✅ MONGODB_URI" || echo -e "   ❌ MONGODB_URI (OBLIGATORIA)"  
grep -q "^OPENAI_API_KEY=" .env && echo -e "   ✅ OPENAI_API_KEY" || echo -e "   ❌ OPENAI_API_KEY (OBLIGATORIA)"

echo -e "\n${BLUE}🚀 Listo para desarrollo con configuración optimizada!${NC}"
