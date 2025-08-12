# 🔐 Guía de Configuración de Variables de Entorno

## 📋 **Resumen de Archivos .env**

Este proyecto utiliza múltiples archivos `.env` para configurar de manera segura todas las credenciales y configuraciones. Cada servicio tiene su archivo `.env.example` que puedes copiar y configurar.

### 📁 **Estructura de Archivos de Configuración**

```
ArquitecturaTutorial/
├── .env.example                          # ✅ Configuración global principal
├── microservices/
│   ├── auth-service/.env.example         # ✅ JWT + MongoDB
│   ├── chat-service/.env.example         # ✅ OpenAI + Claude + DeepSeek + Gemini
│   ├── history-service/.env.example      # ✅ MongoDB + búsquedas
│   ├── payment-service/.env.example      # ✅ Stripe + MercadoPago
│   └── cache-service/.env.example        # ✅ Redis Cloud
├── frontend/.env.example                 # ✅ Next.js + API URLs
└── setup_env_files.sh                   # ✅ Script de configuración automática
```

## 🚀 **Setup Rápido (COPY-PASTE LISTO)**

### 1️⃣ **Paso 1: Configurar archivo global**

```bash
# Copiar archivo principal
cp .env.example .env

# Editar con tus credenciales reales
nano .env  # o tu editor preferido
```

### 2️⃣ **Paso 2: Ejecutar script automático**

```bash
# Hacer ejecutable y ejecutar
chmod +x setup_env_files.sh
./setup_env_files.sh
```

¡Listo! Todos los archivos .env estarán configurados automáticamente.

---

## 🔑 **Credenciales que DEBES Configurar**

### 🎯 **OBLIGATORIAS (el proyecto no funciona sin estas)**

#### **MongoDB Atlas** (Base de Datos)
```bash
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
```
📌 **Dónde conseguir**: [MongoDB Atlas](https://www.mongodb.com/atlas) (Gratis)

#### **JWT Secret Key** (Autenticación)
```bash
JWT_SECRET_KEY=tu_clave_super_secreta_minimo_32_caracteres_cambiar_en_produccion
```
📌 **Genera una**: `openssl rand -hex 32` o [generador online](https://generate-secret.vercel.app/32)

#### **OpenAI API Key** (Chat Principal)
```bash
OPENAI_API_KEY=sk-tu-api-key-de-openai-aqui
```
📌 **Dónde conseguir**: [OpenAI Platform](https://platform.openai.com/api-keys)

### 🎨 **OPCIONALES (para funcionalidades completas)**

#### **Claude API** (Anthropic)
```bash
CLAUDE_API_KEY=sk-ant-tu-api-key-de-claude-aqui
```
📌 **Dónde conseguir**: [Anthropic Console](https://console.anthropic.com/)

#### **DeepSeek API**
```bash
DEEPSEEK_API_KEY=tu-api-key-de-deepseek-aqui
```
📌 **Dónde conseguir**: [DeepSeek Platform](https://platform.deepseek.com/)

#### **Google Gemini API**
```bash
GEMINI_API_KEY=tu-api-key-de-gemini-aqui
```
📌 **Dónde conseguir**: [Google AI Studio](https://aistudio.google.com/app/apikey)

#### **Redis Cloud** (Caché)
```bash
REDIS_URL=redis://default:password@redis-url:port
```
📌 **Dónde conseguir**: [Redis Cloud](https://redis.com/redis-enterprise-cloud/) (Gratis 30MB)

#### **Stripe** (Pagos - SANDBOX)
```bash
STRIPE_SECRET_KEY=sk_test_tu_clave_secreta_de_stripe
STRIPE_PUBLISHABLE_KEY=pk_test_tu_clave_publica_de_stripe
```
📌 **Dónde conseguir**: [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)

#### **MercadoPago** (Pagos - SANDBOX)
```bash
MERCADOPAGO_ACCESS_TOKEN=TEST-tu-token-de-mercadopago
MERCADOPAGO_PUBLIC_KEY=TEST-tu-clave-publica-de-mp
```
📌 **Dónde conseguir**: [MercadoPago Developers](https://www.mercadopago.com/developers/)

---

## 📝 **Configuración Detallada por Archivo**

### 🌐 **Archivo Global (/.env)**

Este es el archivo PRINCIPAL que contiene todas las credenciales:

```bash
# =================================================
# CREDENCIALES PRINCIPALES (OBLIGATORIAS)
# =================================================
JWT_SECRET_KEY=cambiar_por_clave_segura_32_caracteres_minimo
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
OPENAI_API_KEY=sk-tu-api-key-de-openai

# =================================================
# CREDENCIALES OPCIONALES
# =================================================
CLAUDE_API_KEY=sk-ant-api-key-opcional
DEEPSEEK_API_KEY=api-key-opcional  
GEMINI_API_KEY=api-key-opcional
REDIS_URL=redis://default:password@redis-url:port

# =================================================
# PAGOS (SANDBOX/TEST SOLAMENTE)
# =================================================
STRIPE_SECRET_KEY=sk_test_clave_de_prueba
STRIPE_PUBLISHABLE_KEY=pk_test_clave_publica
MERCADOPAGO_ACCESS_TOKEN=TEST-token-de-prueba
```

### 🔐 **Auth Service (microservices/auth-service/.env)**

Enfocado en autenticación y usuarios:

```bash
# JWT Configuration
JWT_SECRET_KEY=tu_clave_jwt_secreta
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_auth
USERS_COLLECTION=users

# Security
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
```

### 🤖 **Chat Service (microservices/chat-service/.env)**

Configuración para todos los LLMs:

```bash
# LLM API Keys
OPENAI_API_KEY=sk-tu-openai-key
CLAUDE_API_KEY=sk-ant-tu-claude-key
DEEPSEEK_API_KEY=tu-deepseek-key
GEMINI_API_KEY=tu-gemini-key

# LLM Configuration
DEFAULT_LLM=openai
MAX_TOKENS_DEFAULT=4000
TEMPERATURE_DEFAULT=0.7
ENABLE_STREAMING=true

# Rate Limiting por plan
FREE_REQUESTS_PER_HOUR=50
PREMIUM_REQUESTS_PER_HOUR=500
ENTERPRISE_REQUESTS_PER_HOUR=5000
```

### 📚 **History Service (microservices/history-service/.env)**

Para gestión de conversaciones:

```bash
# Database Configuration
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
DATABASE_NAME=llm_wrapper_history
CONVERSATIONS_COLLECTION=conversations

# Pagination and Limits
MAX_CONVERSATIONS_PER_USER=1000
DEFAULT_PAGE_SIZE=20
MAX_MESSAGE_LENGTH=50000

# Search Configuration
ENABLE_FULL_TEXT_SEARCH=true
MAX_SEARCH_RESULTS=50
```

### 💳 **Payment Service (microservices/payment-service/.env)**

Integración con Stripe y MercadoPago:

```bash
# Stripe Configuration (SANDBOX)
STRIPE_SECRET_KEY=sk_test_tu_stripe_secret
STRIPE_PUBLISHABLE_KEY=pk_test_tu_stripe_public
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret

# MercadoPago Configuration (SANDBOX)
MERCADOPAGO_ACCESS_TOKEN=TEST-tu-mp-token
MERCADOPAGO_PUBLIC_KEY=TEST-tu-mp-public
MERCADOPAGO_ENVIRONMENT=sandbox

# Pricing (en centavos)
PREMIUM_PLAN_PRICE_MONTHLY=999  # $9.99
ENTERPRISE_PLAN_PRICE_MONTHLY=4999  # $49.99
```

### ⚡ **Cache Service (microservices/cache-service/.env)**

Configuración Redis:

```bash
# Redis Configuration
REDIS_URL=redis://default:password@redis-url:port
REDIS_HOST=redis-cloud-url
REDIS_PORT=6379
REDIS_PASSWORD=tu-redis-password
REDIS_SSL=true

# Cache TTL (en segundos)
DEFAULT_CACHE_TTL=3600          # 1 hora
SESSION_CACHE_TTL=86400         # 24 horas
CHAT_RESPONSE_CACHE_TTL=7200    # 2 horas
```

### 🎨 **Frontend (frontend/.env.local)**

Configuración Next.js:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_CHAT_SERVICE_URL=http://localhost:8002

# App Configuration
NEXT_PUBLIC_APP_NAME="LLM Wrapper"
NEXT_PUBLIC_DEFAULT_LLM=openai
NEXT_PUBLIC_ENABLE_STREAMING=true

# Payment Integration (Client-side)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_tu_stripe_public
NEXT_PUBLIC_MERCADOPAGO_PUBLIC_KEY=TEST-tu-mp-public

# Features Flags
NEXT_PUBLIC_ENABLE_REGISTRATION=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

---

## 🔒 **Seguridad y Mejores Prácticas**

### ✅ **DO's (HACER)**

1. **Usar claves de SANDBOX/TEST** para desarrollo
2. **Generar JWT_SECRET_KEY fuerte** (mínimo 32 caracteres)
3. **Crear bases de datos separadas** por environment
4. **Usar .env.local en frontend** (Next.js específico)
5. **Revisar que .gitignore incluye** archivos .env

### ❌ **DON'Ts (NO HACER)**

1. **NUNCA** subir archivos .env a Git
2. **NUNCA** usar claves de producción en desarrollo
3. **NUNCA** hardcodear credenciales en el código
4. **NUNCA** compartir archivos .env por email/chat
5. **NUNCA** usar la misma JWT_SECRET_KEY por defecto

### 🛡️ **Verificaciones de Seguridad**

```bash
# Verificar que .env está en .gitignore
cat .gitignore | grep .env

# Verificar que no hay archivos .env en Git
git status --ignored

# Generar nueva JWT_SECRET_KEY
openssl rand -hex 32

# Verificar conexión MongoDB
mongo "tu_mongodb_uri" --eval "db.runCommand({connectionStatus: 1})"
```

---

## 🚨 **Solución de Problemas Comunes**

### ❌ **"JWT_SECRET_KEY is too short"**
```bash
# Generar clave de 32+ caracteres
JWT_SECRET_KEY=$(openssl rand -hex 32)
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env
```

### ❌ **"MongoDB connection failed"**
```bash
# Verificar formato correcto
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/basededatos
# NO olvides incluir el nombre de la base de datos al final
```

### ❌ **"OpenAI API key invalid"**
```bash
# Verificar formato correcto (debe empezar con sk-)
OPENAI_API_KEY=sk-tu-api-key-completa-aqui
# Verificar que la key tiene créditos disponibles
```

### ❌ **"Redis connection timeout"**
```bash
# Verificar formato con credenciales
REDIS_URL=redis://default:tu_password@tu_host:puerto
# Verificar que SSL esté habilitado si es necesario
REDIS_SSL=true
```

### ❌ **"Stripe webhook signature mismatch"**
```bash
# Usar endpoint local para webhooks en desarrollo
# O usar Stripe CLI: stripe listen --forward-to localhost:8003/webhooks/stripe
```

---

## 🎯 **Quick Start Checklist**

### Configuración Mínima (MVP funcional):

- [ ] ✅ **Copiar** `.env.example` a `.env`
- [ ] 🔑 **MongoDB Atlas** URI configurada
- [ ] 🔒 **JWT_SECRET_KEY** generada (32+ chars)
- [ ] 🤖 **OpenAI API Key** configurada
- [ ] 🚀 **Ejecutar** `./setup_env_files.sh`
- [ ] ⚡ **Probar** conexiones básicas

### Configuración Completa (Todas las features):

- [ ] 🤖 **Claude API** configurada
- [ ] 🧠 **DeepSeek API** configurada  
- [ ] 🔮 **Gemini API** configurada
- [ ] ⚡ **Redis Cloud** configurado
- [ ] 💳 **Stripe SANDBOX** configurado
- [ ] 🏦 **MercadoPago TEST** configurado
- [ ] 📧 **SMTP** configurado (opcional)

---

## 📞 **Soporte**

Si tienes problemas con la configuración:

1. **Revisa este archivo** - contiene todas las respuestas
2. **Ejecuta el script automático** - `./setup_env_files.sh`
3. **Verifica los .env.example** - tienen valores por defecto
4. **Consulta la documentación** de cada proveedor (MongoDB, OpenAI, etc.)

---

**🎉 ¡Con esta configuración tendrás todo listo para development en minutos!**
