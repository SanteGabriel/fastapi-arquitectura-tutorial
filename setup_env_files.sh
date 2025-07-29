#!/bin/bash

# 🔧 Script para crear archivos .env desde las plantillas .env.example
# Este script copia los archivos .env.example a .env para cada microservicio

set -e

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

print_status "🔧 Creando archivos .env desde plantillas..."

# Array de servicios
services=("auth-service" "chat-service" "payment-service" "history-service")

for service in "${services[@]}"
do
    service_path="microservices/$service"
    example_file="$service_path/.env.example"
    env_file="$service_path/.env"
    
    if [ ! -f "$example_file" ]; then
        print_warning "No se encontró $example_file. Saltando $service..."
        continue
    fi
    
    if [ -f "$env_file" ]; then
        print_warning "El archivo $env_file ya existe."
        read -p "¿Sobrescribirlo? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Saltando $service..."
            continue
        fi
    fi
    
    # Copiar archivo
    cp "$example_file" "$env_file"
    print_success "✅ Creado $env_file"
done

echo ""
print_success "🎉 Archivos .env creados exitosamente!"
echo ""
print_warning "⚠️  IMPORTANTE: Debes configurar las siguientes variables:"
echo ""

print_status "🔐 AUTH SERVICE (.env):"
echo "   • JWT_SECRET_KEY - Cambia por una clave secreta fuerte"
echo "   • MONGODB_URI - Tu conexión a MongoDB Atlas"
echo ""

print_status "🤖 CHAT SERVICE (.env):"
echo "   • OPENAI_API_KEY - Tu API key de OpenAI"
echo "   • CLAUDE_API_KEY - Tu API key de Anthropic"
echo "   • DEEPSEEK_API_KEY - Tu API key de DeepSeek"
echo "   • GEMINI_API_KEY - Tu API key de Google AI"
echo ""

print_status "💳 PAYMENT SERVICE (.env):"
echo "   • STRIPE_SECRET_KEY - Tu clave secreta de Stripe"
echo "   • STRIPE_PUBLISHABLE_KEY - Tu clave pública de Stripe"
echo "   • MERCADOPAGO_ACCESS_TOKEN - Tu token de MercadoPago"
echo ""

print_status "📚 HISTORY SERVICE (.env):"
echo "   • MONGODB_URI - Tu conexión a MongoDB Atlas"
echo ""

print_status "🚀 Próximos pasos:"
echo "   1. Edita cada archivo .env con tus credenciales reales"
echo "   2. NUNCA subas archivos .env a Git (ya están en .gitignore)"
echo "   3. Ejecuta ./start_dev.sh para iniciar los servicios"
echo ""

print_status "💡 Comandos útiles:"
echo "   • Editar auth service: nano microservices/auth-service/.env"
echo "   • Editar chat service: nano microservices/chat-service/.env"
echo "   • Ver todos los .env: ls microservices/*/.env"
echo ""

print_success "🔥 ¡Listo para configurar tus credenciales!" 