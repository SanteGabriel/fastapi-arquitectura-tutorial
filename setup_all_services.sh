#!/bin/bash

# 🚀 Setup Script para LLM Wrapper Web Microservicios
# Este script crea y configura entornos virtuales para todos los microservicios

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -d "microservices" ]; then
    print_error "No se encontró el directorio 'microservices'. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

print_status "🚀 Iniciando configuración de microservicios LLM Wrapper Web..."

# Array de servicios con FastAPI
services=("auth-service" "chat-service" "payment-service" "history-service")

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_status "Usando Python $python_version"

# Configurar cada microservicio
for service in "${services[@]}"
do
    print_status "📦 Configurando $service..."
    
    # Verificar que el directorio existe
    if [ ! -d "microservices/$service" ]; then
        print_warning "Directorio microservices/$service no existe. Saltando..."
        continue
    fi
    
    # Verificar que requirements.txt existe
    if [ ! -f "microservices/$service/requirements.txt" ]; then
        print_warning "No se encontró requirements.txt en $service. Saltando..."
        continue
    fi
    
    # Cambiar al directorio del servicio
    cd "microservices/$service"
    
    # Eliminar venv existente si existe
    if [ -d ".venv" ]; then
        print_warning "Eliminando entorno virtual existente en $service..."
        rm -rf .venv
    fi
    
    # Crear nuevo entorno virtual
    print_status "Creando entorno virtual para $service..."
    python3 -m venv .venv
    
    # Activar entorno virtual
    source .venv/bin/activate
    
    # Actualizar pip
    print_status "Actualizando pip en $service..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Instalar dependencias
    print_status "Instalando dependencias para $service..."
    pip install -r requirements.txt
    
    # Verificar instalación
    installed_packages=$(pip list --format=freeze | wc -l)
    print_success "✅ $service configurado - $installed_packages paquetes instalados"
    
    # Desactivar entorno virtual
    deactivate
    
    # Volver al directorio raíz
    cd ../..
done

# Configurar shared utilities si es necesario
if [ -d "shared" ]; then
    print_status "📚 Configurando shared utilities..."
    
    # Crear __init__.py si no existe
    if [ ! -f "shared/__init__.py" ]; then
        touch shared/__init__.py
        print_status "Creado shared/__init__.py"
    fi
    
    # Crear setup.py para shared si no existe
    if [ ! -f "shared/setup.py" ]; then
        cat > shared/setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="llm-wrapper-shared",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "pydantic>=2.5.0",
        "PyJWT>=2.8.0",
        "motor>=3.3.2",
        "redis>=5.0.1"
    ],
    description="Shared utilities for LLM Wrapper microservices",
    author="Your Name",
    python_requires=">=3.8",
)
EOF
        print_status "Creado shared/setup.py"
    fi
    
    print_success "✅ Shared utilities configurado"
fi

# Crear archivos .env de ejemplo
print_status "📄 Creando archivos .env de ejemplo..."

# Auth Service .env.example
cat > microservices/auth-service/.env.example << EOF
# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_auth
USERS_COLLECTION=users
SESSIONS_COLLECTION=sessions
SUBSCRIPTIONS_COLLECTION=subscriptions

# Security
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=1
EOF

# Chat Service .env.example
cat > microservices/chat-service/.env.example << EOF
# LLM API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
CLAUDE_API_KEY=sk-ant-your-claude-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# LLM Configuration
DEFAULT_LLM=openai
MAX_TOKENS_DEFAULT=4000
TEMPERATURE_DEFAULT=0.7
ENABLE_STREAMING=true

# Rate Limiting
FREE_REQUESTS_PER_HOUR=50
PREMIUM_REQUESTS_PER_HOUR=500
ENTERPRISE_REQUESTS_PER_HOUR=5000

# Failover Configuration
ENABLE_FALLBACK=true
FALLBACK_ORDER=openai,claude,deepseek,gemini
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=2
EOF

# Payment Service .env.example
cat > microservices/payment-service/.env.example << EOF
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_PREMIUM=price_premium_monthly_id
STRIPE_PRICE_ENTERPRISE=price_enterprise_monthly_id

# MercadoPago Configuration
MERCADOPAGO_ACCESS_TOKEN=your_mp_access_token
MERCADOPAGO_PUBLIC_KEY=your_mp_public_key
MERCADOPAGO_WEBHOOK_SECRET=your_mp_webhook_secret
MERCADOPAGO_CLIENT_ID=your_mp_client_id
MERCADOPAGO_CLIENT_SECRET=your_mp_client_secret

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_payments

# Business Logic
DEFAULT_TRIAL_DAYS=7
GRACE_PERIOD_DAYS=3
AUTO_RETRY_FAILED_PAYMENTS=true
SEND_EMAIL_NOTIFICATIONS=true
EOF

# History Service .env.example
cat > microservices/history-service/.env.example << EOF
# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_history
CONVERSATIONS_COLLECTION=conversations
MESSAGES_COLLECTION=messages
EXPORTS_COLLECTION=exports

# Search Configuration
ENABLE_FULL_TEXT_SEARCH=true
SEARCH_INDEX_NAME=conversation_search
MAX_SEARCH_RESULTS=100
SEARCH_TIMEOUT_SECONDS=10

# Retention Policies (days)
FREE_RETENTION_DAYS=30
PREMIUM_RETENTION_DAYS=365
ENTERPRISE_RETENTION_DAYS=0

# Export Configuration
EXPORT_MAX_FILE_SIZE_MB=100
EXPORT_TTL_HOURS=24
EXPORT_STORAGE_PATH=/tmp/exports
ENABLE_EXPORT_COMPRESSION=true
EOF

print_success "✅ Archivos .env.example creados"

# Crear script de desarrollo
cat > start_dev.sh << 'EOF'
#!/bin/bash

# Script para iniciar todos los servicios en desarrollo
# Cada servicio se ejecuta en su propio puerto

services=("auth-service:8001" "chat-service:8002" "payment-service:8003" "history-service:8004")

echo "🚀 Iniciando todos los microservicios..."

for service_port in "${services[@]}"
do
    service=${service_port%:*}
    port=${service_port#*:}
    
    echo "📦 Iniciando $service en puerto $port..."
    
    # Abrir nueva terminal y ejecutar el servicio
    osascript -e "tell app \"Terminal\" to do script \"cd $(pwd)/microservices/$service && source .venv/bin/activate && uvicorn main:app --reload --port $port\""
done

echo "✅ Todos los servicios iniciados!"
echo "📍 URLs de servicios:"
echo "   • Auth Service: http://localhost:8001"
echo "   • Chat Service: http://localhost:8002"
echo "   • Payment Service: http://localhost:8003"
echo "   • History Service: http://localhost:8004"
EOF

chmod +x start_dev.sh

print_success "✅ Script de desarrollo creado (start_dev.sh)"

# Resumen final
echo ""
print_success "🎉 ¡Configuración completada exitosamente!"
echo ""
print_status "📋 Resumen:"
echo "   • Entornos virtuales creados para todos los microservicios"
echo "   • Dependencias instaladas"
echo "   • Archivos .env.example creados"
echo "   • Script de desarrollo creado"
echo ""
print_status "🚀 Próximos pasos:"
echo "   1. Copia y configura los archivos .env:"
echo "      cp microservices/auth-service/.env.example microservices/auth-service/.env"
echo "   2. Agrega tus API keys y configuraciones"
echo "   3. Ejecuta ./start_dev.sh para iniciar todos los servicios"
echo ""
print_status "💡 Para desarrollar un servicio individual:"
echo "      cd microservices/auth-service"
echo "      source .venv/bin/activate"
echo "      uvicorn main:app --reload --port 8001"
echo ""
print_success "🔥 ¡Listo para comenzar el desarrollo!" 