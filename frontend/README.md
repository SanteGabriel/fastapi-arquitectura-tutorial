# LLM Wrapper Frontend

Frontend moderno y responsivo para el sistema LLM Wrapper Web construido con Next.js, TypeScript y Tailwind CSS.

## 🚀 Características

- **Diseño Responsivo**: Optimizado para móviles, tablets y escritorio
- **Framework Moderno**: Next.js 15 con App Router
- **TypeScript**: Tipado estático para mayor robustez
- **Tailwind CSS**: Estilos utilitarios para un diseño consistente
- **Framer Motion**: Animaciones suaves y profesionales
- **Zustand**: Gestión de estado simple y eficiente
- **Axios**: Cliente HTTP para comunicación con APIs

## 🛠️ Tecnologías

- **Framework**: Next.js 15.4.6
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS 4
- **Animaciones**: Framer Motion
- **Estado**: Zustand
- **Iconos**: Lucide React
- **HTTP**: Axios
- **UI**: Headless UI

## 🚦 Scripts Disponibles

```bash
# Desarrollo
npm run dev           # Inicia el servidor de desarrollo (puerto 3000)

# Producción
npm run build         # Construye la aplicación para producción
npm run start         # Inicia la aplicación en modo producción

# Calidad de código
npm run lint          # Ejecuta ESLint
```

## 🔧 Configuración

### Variables de Entorno

El archivo `.env.local` contiene las configuraciones del entorno:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_CHAT_SERVICE_URL=http://localhost:8002
NEXT_PUBLIC_PAYMENT_SERVICE_URL=http://localhost:8003
NEXT_PUBLIC_HISTORY_SERVICE_URL=http://localhost:8004

# App Configuration
NEXT_PUBLIC_APP_NAME="LLM Wrapper Web"
NEXT_PUBLIC_APP_VERSION="1.0.0"

# Features
NEXT_PUBLIC_ENABLE_STRIPE=true
NEXT_PUBLIC_ENABLE_MERCADOPAGO=true
NEXT_PUBLIC_ENABLE_STREAMING=true
```

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 13+)
│   │   ├── login/             # Página de login
│   │   ├── register/          # Página de registro (por crear)
│   │   ├── chat/              # Interfaz de chat (por crear)
│   │   ├── globals.css        # Estilos globales
│   │   ├── layout.tsx         # Layout principal
│   │   └── page.tsx           # Homepage
│   ├── components/            # Componentes reutilizables
│   │   ├── ui/               # Componentes base
│   │   │   ├── Button.tsx    # Botón personalizable
│   │   │   └── Input.tsx     # Input con validación
│   │   ├── layout/           # Componentes de layout
│   │   │   └── Navbar.tsx    # Barra de navegación
│   │   ├── auth/             # Componentes de autenticación
│   │   ├── chat/             # Componentes del chat
│   │   ├── payment/          # Componentes de pagos
│   │   └── history/          # Componentes del historial
│   ├── store/                # Gestión de estado
│   │   ├── authStore.ts      # Estado de autenticación
│   │   └── chatStore.ts      # Estado del chat
│   ├── types/                # Definiciones de TypeScript
│   │   └── index.ts          # Tipos principales
│   ├── lib/                  # Utilidades y configuración
│   └── hooks/                # Hooks personalizados
├── public/                   # Archivos estáticos
├── .env.local               # Variables de entorno
├── package.json             # Dependencias y scripts
└── README.md               # Este archivo
```

## 🎨 Diseño y UX

### Paleta de Colores
- **Primario**: Azul (#3B82F6) - Botones principales, enlaces
- **Secundario**: Púrpura (#8B5CF6) - Gradientes, acentos
- **Éxito**: Verde (#10B981) - Confirmaciones
- **Error**: Rojo (#EF4444) - Errores y advertencias
- **Neutro**: Grises - Texto, fondos, bordes

### Breakpoints Responsivos
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px  
- **Desktop**: > 1024px

## 🔐 Autenticación

El sistema de autenticación incluye:

- **Login/Registro**: Formularios con validación
- **JWT Tokens**: Almacenados en localStorage
- **Protección de rutas**: Middleware automático
- **Refresh tokens**: Renovación automática
- **Estado persistente**: Zustand con persist

## 📱 Responsive Design

El frontend está optimizado para:

### Mobile First
- Diseño optimizado para móviles
- Navegación tipo hamburger
- Touch-friendly interactions
- Viewport adaptable

### Tablet & Desktop
- Layouts multi-columna
- Navegación horizontal
- Hover states avanzados
- Sidebars y modals

## 🔗 Integración con Backend

El frontend se comunica con los microservicios:

- **Auth Service** (8001): Login, registro, perfil
- **Chat Service** (8002): Mensajes, conversaciones
- **Payment Service** (8003): Suscripciones, pagos
- **History Service** (8004): Historial, exportaciones

## 📋 Estado Actual

✅ **Completado:**
- Estructura base del proyecto
- Página principal (homepage)
- Sistema de autenticación (stores)
- Componentes UI básicos (Button, Input)
- Navegación responsiva
- Página de login
- Configuración de TypeScript y ESLint

🔄 **En Progreso:**
- Página de registro
- Interfaz de chat
- Páginas de historial y configuración

📋 **Por Hacer:**
- Sistema de pagos
- Dashboard de analytics
- Modo oscuro
- PWA features
- Tests unitarios

## 🌐 Deployment

Para desplegar en producción:

```bash
npm run build
npm run start
```

O usar plataformas como:
- **Vercel** (recomendado para Next.js)
- **Netlify**
- **AWS Amplify**
- **Docker**

---

**Estado**: 🔄 En desarrollo activo  
**Version**: 1.0.0  
**Puerto**: 3000 (desarrollo)
