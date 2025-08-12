#!/bin/bash

# 🚀 Script de configuración rápida para Backend LLM Wrapper
# Este script configura los microservicios principales implementados

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "🚀 Configurando Backend LLM Wrapper..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi

print_status "✅ Python $(python3 --version | cut -d' ' -f2) detectado"

# Servicios a configurar
services=("auth-service" "chat-service")

for service in "${services[@]}"
do
    print_status "📦 Configurando $service..."
    
    if [ ! -d "microservices/$service" ]; then
        print_warning "Directorio microservices/$service no existe"
        continue
    fi
    
    cd "microservices/$service"
    
    # Eliminar venv existente
    if [ -d ".venv" ]; then
        print_status "🗑️ Eliminando entorno virtual existente..."
        rm -rf .venv
    fi
    
    # Crear entorno virtual
    print_status "🔨 Creando entorno virtual..."
    python3 -m venv .venv
    
    # Activar entorno virtual
    source .venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Instalar dependencias base
    print_status "📚 Instalando dependencias..."
    
    if [ "$service" = "auth-service" ]; then
        pip install fastapi uvicorn pydantic pydantic-settings motor pymongo bcrypt PyJWT python-multipart email-validator
    elif [ "$service" = "chat-service" ]; then
        pip install fastapi uvicorn pydantic pydantic-settings openai httpx aiohttp tenacity
    fi
    
    # Crear archivo requirements.txt
    pip freeze > requirements.txt
    
    # Crear archivo .env desde .env.example
    if [ -f ".env.example" ] && [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "📄 Archivo .env creado desde plantilla"
    fi
    
    deactivate
    cd ../..
    
    print_success "✅ $service configurado correctamente"
done

# Crear archivo de configuración global
print_status "⚙️ Creando configuración global..."

cat > start_services.sh << 'EOF'
#!/bin/bash

# Script para iniciar los microservicios implementados

services=(
    "auth-service:8001"
    "chat-service:8002"
)

echo "🚀 Iniciando microservicios LLM Wrapper..."

for service_port in "${services[@]}"
do
    service=${service_port%:*}
    port=${service_port#*:}
    
    echo "📦 Iniciando $service en puerto $port..."
    
    # Verificar si el servicio existe
    if [ ! -f "microservices/$service/main.py" ]; then
        echo "❌ $service no implementado todavía"
        continue
    fi
    
    # Iniciar en nueva terminal
    osascript -e "tell app \"Terminal\" to do script \"cd $(pwd)/microservices/$service && source .venv/bin/activate && python main.py\""
done

echo ""
echo "✅ Servicios iniciados en terminales separadas!"
echo ""
echo "📍 URLs de servicios implementados:"
echo "   • Auth Service: http://localhost:8001"
echo "   • Chat Service: http://localhost:8002"
echo ""
echo "📖 Documentación interactiva:"
echo "   • Auth API: http://localhost:8001/docs"
echo "   • Chat API: http://localhost:8002/docs"
echo ""
echo "🔧 Para configurar:"
echo "   1. Edita los archivos .env en cada servicio"
echo "   2. Configura tu MongoDB URI"
echo "   3. Agrega tus API keys de LLMs"
EOF

chmod +x start_services.sh

# Resumen final
echo ""
print_success "🎉 ¡Configuración completada!"
echo ""
print_status "📋 Servicios implementados:"
echo "   ✅ Auth Service - Autenticación JWT + MongoDB"
echo "   ✅ Chat Service - Integración OpenAI + Rate Limiting"
echo "   ✅ Shared Libraries - Modelos, excepciones, middleware"
echo ""
print_status "📋 Servicios pendientes:"
echo "   ⏳ History Service - Gestión de conversaciones"
echo "   ⏳ Payment Service - Stripe + MercadoPago"
echo "   ⏳ Cache Service - Redis para caché"
echo ""
print_status "🚀 Próximos pasos:"
echo "   1. Configura MongoDB Atlas:"
echo "      - Crea cluster en https://cloud.mongodb.com"
echo "      - Copia connection string a los archivos .env"
echo ""
echo "   2. Configura OpenAI API:"
echo "      - Obtén API key en https://platform.openai.com"
echo "      - Agrégala a microservices/chat-service/.env"
echo ""
echo "   3. Inicia los servicios:"
echo "      ./start_services.sh"
echo ""
echo "   4. Prueba las APIs:"
echo "      curl http://localhost:8001/health"
echo "      curl http://localhost:8002/health"
echo ""
print_success "🔥 ¡Todo listo para desarrollo!"
