#!/bin/bash

# =================================================
# ENV SETUP SCRIPT - LLM WRAPPER PROJECT
# =================================================
# Este script copia el archivo .env global a todos los servicios
# y crea archivos .env individuales con las configuraciones específicas

set -e

# Colors para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    LLM WRAPPER - ENV SETUP SCRIPT     ${NC}"
echo -e "${BLUE}========================================${NC}"

# Verificar que existe el archivo .env global
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo .env en el directorio raíz${NC}"
    echo -e "${YELLOW}💡 Por favor:${NC}"
    echo -e "   1. Copia .env.example a .env"
    echo -e "   2. Rellena todas las API keys y credenciales"
    echo -e "   3. Ejecuta este script nuevamente"
    echo ""
    echo -e "${BLUE}Comando rápido:${NC}"
    echo -e "   cp .env.example .env"
    echo -e "   nano .env  # o tu editor preferido"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env global encontrado${NC}"

# Función para crear .env específico de cada servicio
create_service_env() {
    local service_path=$1
    local service_name=$2
    
    echo -e "${BLUE}📁 Configurando $service_name...${NC}"
    
    # Crear directorio si no existe
    mkdir -p "$service_path"
    
    # Copiar .env global al servicio
    cp .env "$service_path/.env"
    
    # Verificar que el archivo .env.example existe
    if [ -f "$service_path/.env.example" ]; then
        echo -e "${GREEN}   ✅ .env creado para $service_name${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Advertencia: No hay .env.example para $service_name${NC}"
    fi
}

# Crear .env para cada microservicio
echo -e "\n${BLUE}🔧 Configurando microservicios...${NC}"

create_service_env "microservices/auth-service" "Auth Service"
create_service_env "microservices/chat-service" "Chat Service"
create_service_env "microservices/history-service" "History Service"
create_service_env "microservices/payment-service" "Payment Service"
create_service_env "microservices/cache-service" "Cache Service"

# Configurar frontend
echo -e "\n${BLUE}🎨 Configurando frontend...${NC}"
if [ -d "frontend" ]; then
    # Para Next.js, crear .env.local desde el .env global
    if [ -f "frontend/.env.example" ]; then
        # Extraer solo las variables NEXT_PUBLIC_ del ejemplo
        # y agregar las del .env global que sean necesarias
        cp frontend/.env.example frontend/.env.local
        
        # Agregar configuraciones específicas del .env global al frontend
        echo "" >> frontend/.env.local
        echo "# Auto-generated from global .env" >> frontend/.env.local
        grep "STRIPE_PUBLISHABLE_KEY" .env >> frontend/.env.local || true
        grep "MERCADOPAGO_PUBLIC_KEY" .env >> frontend/.env.local || true
        
        echo -e "${GREEN}   ✅ .env.local creado para Frontend${NC}"
    else
        echo -e "${YELLOW}   ⚠️  No hay .env.example para Frontend${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  Directorio frontend no encontrado${NC}"
fi

# Configurar shared
echo -e "\n${BLUE}📚 Configurando shared utilities...${NC}"
create_service_env "shared" "Shared Libraries"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}    ✅ CONFIGURACIÓN COMPLETADA        ${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}📋 Resumen de archivos creados:${NC}"
echo -e "   📁 microservices/auth-service/.env"
echo -e "   📁 microservices/chat-service/.env"
echo -e "   📁 microservices/history-service/.env"
echo -e "   📁 microservices/payment-service/.env"
echo -e "   📁 microservices/cache-service/.env"
echo -e "   📁 shared/.env"
echo -e "   📁 frontend/.env.local"

echo -e "\n${YELLOW}⚠️  IMPORTANTE - Verificaciones de seguridad:${NC}"
echo -e "   1. Revisa que todas las API keys estén configuradas"
echo -e "   2. Cambia JWT_SECRET_KEY por una clave segura (min. 32 caracteres)"
echo -e "   3. Verifica las conexiones a MongoDB Atlas y Redis Cloud"
echo -e "   4. Confirma que las claves de Stripe/MercadoPago sean de SANDBOX/TEST"

echo -e "\n${BLUE}🚀 Próximos pasos:${NC}"
echo -e "   1. cd microservices/auth-service && source .venv/bin/activate"
echo -e "   2. uvicorn main:app --reload --port 8001"
echo -e "   3. Probar endpoints en http://localhost:8001/docs"

echo -e "\n${GREEN}🎉 ¡Todo listo para desarrollo!${NC}"
