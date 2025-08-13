#!/bin/bash

# 🚀 Setup Script para LLM Wrapper Web Microservicios - VERSIÓN CORREGIDA
# Este script configura SOLO los microservicios que están realmente implementados

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

print_status "🚀 Configurando microservicios LLM Wrapper Web..."

# ✅ SERVICIOS IMPLEMENTADOS (tienen main.py)
implemented_services=("auth-service" "chat-service")

# ⏳ SERVICIOS PENDIENTES (solo README + requirements.txt)
pending_services=("payment-service" "history-service" "cache-service")

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_status "Usando Python $python_version"

# Configurar servicios IMPLEMENTADOS
echo ""
print_status "📦 Configurando servicios IMPLEMENTADOS..."

for service in "${implemented_services[@]}"
do
    print_status "✅ Configurando $service (IMPLEMENTADO)..."
    
    # Verificar que el directorio y main.py existen
    if [ ! -d "microservices/$service" ] || [ ! -f "microservices/$service/main.py" ]; then
        print_warning "❌ $service no está completamente implementado. Saltando..."
        continue
    fi
    
    # Verificar que requirements.txt existe
    if [ ! -f "microservices/$service/requirements.txt" ]; then
        print_warning "No se encontró requirements.txt en $service. Saltando..."
        continue
    fi
    
    # Cambiar al directorio del servicio
    cd "microservices/$service"
    
    # Verificar si ya tiene entorno virtual configurado
    if [ -d ".venv" ] && [ -f ".venv/pyvenv.cfg" ]; then
        print_status "🔄 Entorno virtual ya existe en $service. Actualizando dependencias..."
        source .venv/bin/activate
        pip install --upgrade pip > /dev/null 2>&1
        pip install -r requirements.txt > /dev/null 2>&1
        deactivate
    else
        # Crear nuevo entorno virtual
        print_status "🆕 Creando entorno virtual para $service..."
        python3 -m venv .venv
        
        # Activar entorno virtual
        source .venv/bin/activate
        
        # Actualizar pip
        print_status "⬆️ Actualizando pip en $service..."
        pip install --upgrade pip > /dev/null 2>&1
        
        # Instalar dependencias
        print_status "📚 Instalando dependencias para $service..."
        pip install -r requirements.txt
        
        deactivate
    fi
    
    # Verificar instalación
    source .venv/bin/activate
    installed_packages=$(pip list --format=freeze | wc -l)
    deactivate
    
    print_success "✅ $service configurado - $installed_packages paquetes instalados"
    
    # Volver al directorio raíz
    cd ../..
done

# Mostrar estado de servicios PENDIENTES
echo ""
print_status "⏳ Estado de servicios PENDIENTES..."

for service in "${pending_services[@]}"
do
    if [ -d "microservices/$service" ]; then
        if [ -f "microservices/$service/main.py" ]; then
            print_success "🎉 $service ¡YA IMPLEMENTADO! (mover a lista de implementados)"
        else
            print_warning "📋 $service - Solo documentación (falta implementar main.py)"
        fi
    else
        print_error "❌ $service - Directorio no existe"
    fi
done

# Configurar shared utilities si es necesario
if [ -d "shared" ]; then
    echo ""
    print_status "📚 Verificando shared utilities..."
    
    # Crear __init__.py si no existe
    if [ ! -f "shared/__init__.py" ]; then
        touch shared/__init__.py
        print_status "✅ Creado shared/__init__.py"
    fi
    
    # Verificar si ya tiene setup.py
    if [ ! -f "shared/setup.py" ]; then
        print_status "📄 Creando shared/setup.py..."
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
        print_success "✅ Creado shared/setup.py"
    else
        print_status "✅ shared/setup.py ya existe"
    fi
    
    print_success "✅ Shared utilities verificado"
fi

# Verificar archivos .env.example existentes (no sobreescribir)
echo ""
print_status "📄 Verificando archivos .env.example..."

for service in "${implemented_services[@]}"
do
    if [ -f "microservices/$service/.env.example" ]; then
        print_success "✅ .env.example existe en $service"
    else
        print_warning "⚠️  .env.example falta en $service (usar setup_env_files.sh)"
    fi
done

# Crear script de desarrollo mejorado
echo ""
print_status "🛠️ Creando script de desarrollo..."

cat > start_services_implemented.sh << 'EOF'
#!/bin/bash

# Script para iniciar SOLO los servicios IMPLEMENTADOS

# Servicios implementados con sus puertos
services=(
    "auth-service:8001"
    "chat-service:8002"
)

echo "🚀 Iniciando microservicios implementados..."
echo ""

for service_port in "${services[@]}"
do
    service=${service_port%:*}
    port=${service_port#*:}
    
    echo "📦 Verificando $service..."
    
    # Verificar si el servicio existe y está implementado
    if [ ! -f "microservices/$service/main.py" ]; then
        echo "❌ $service no está implementado (falta main.py)"
        continue
    fi
    
    if [ ! -d "microservices/$service/.venv" ]; then
        echo "❌ $service no tiene entorno virtual configurado"
        echo "   💡 Ejecuta: ./setup_all_services_fixed.sh"
        continue
    fi
    
    if [ ! -f "microservices/$service/.env" ]; then
        echo "⚠️  $service no tiene archivo .env"
        echo "   💡 Ejecuta: ./setup_env_files.sh"
        echo "   🔧 O copia: cp microservices/$service/.env.example microservices/$service/.env"
    fi
    
    echo "✅ Iniciando $service en puerto $port..."
    
    # Iniciar en nueva terminal (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell app \"Terminal\" to do script \"cd $(pwd)/microservices/$service && source .venv/bin/activate && uvicorn main:app --reload --port $port\""
    else
        # Para Linux, usar gnome-terminal o xterm
        gnome-terminal -- bash -c "cd $(pwd)/microservices/$service && source .venv/bin/activate && uvicorn main:app --reload --port $port; exec bash" 2>/dev/null || \
        xterm -e "cd $(pwd)/microservices/$service && source .venv/bin/activate && uvicorn main:app --reload --port $port; bash" &
    fi
done

echo ""
echo "✅ Servicios iniciados en terminales separadas!"
echo ""
echo "📍 URLs de servicios implementados:"
echo "   • Auth Service:  http://localhost:8001"
echo "   • Chat Service:  http://localhost:8002"
echo ""
echo "📖 Documentación interactiva:"
echo "   • Auth API:  http://localhost:8001/docs"
echo "   • Chat API:  http://localhost:8002/docs"
echo ""
echo "⏳ Servicios pendientes de implementación:"
echo "   • Payment Service: http://localhost:8003 (pendiente)"
echo "   • History Service: http://localhost:8004 (pendiente)"
echo "   • Cache Service:   http://localhost:6379 (pendiente)"
echo ""
echo "💡 Para implementar más servicios, revisa los READMEs en cada directorio."
EOF

chmod +x start_services_implemented.sh

print_success "✅ Script start_services_implemented.sh creado"

# Resumen final
echo ""
print_success "🎉 ¡Configuración completada!"
echo ""
print_status "📊 Resumen del estado actual:"
echo "   ✅ IMPLEMENTADOS y configurados:"
for service in "${implemented_services[@]}"
do
    echo "      • $service"
done
echo ""
echo "   ⏳ PENDIENTES de implementación:"
for service in "${pending_services[@]}"
do
    echo "      • $service (solo README + requirements.txt)"
done
echo ""
print_status "🚀 Próximos pasos:"
echo "   1. Configurar variables de entorno:"
echo "      ./setup_env_files.sh  # o ./setup_env_smart.sh"
echo ""
echo "   2. Iniciar servicios implementados:"
echo "      ./start_services_implemented.sh"
echo ""
echo "   3. Probar APIs implementadas:"
echo "      curl http://localhost:8001/health  # Auth Service"
echo "      curl http://localhost:8002/health  # Chat Service"
echo ""
echo "   4. Para implementar servicios pendientes:"
echo "      • Revisar microservices/[service]/README.md"
echo "      • Crear main.py basándose en la documentación"
echo ""
print_status "💡 Tip: Usa start_services_implemented.sh en lugar de start_dev.sh"
print_success "🔥 ¡Todo listo para desarrollo con servicios implementados!"
