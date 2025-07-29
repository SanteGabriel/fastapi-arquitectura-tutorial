# 💳 Payment Service - Servicio de Pagos

## 📋 Descripción
Microservicio responsable del procesamiento de pagos, gestión de suscripciones y integración con Stripe y Mercado Pago para el sistema LLM Wrapper Web.

## 🏗️ Arquitectura del Servicio

```
┌─────────────────────────────────────────┐
│             PAYMENT SERVICE             │
│              Puerto: 8003               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Routes    │    │  Middleware │    │
│  │             │    │             │    │
│  │ /subscribe  │◄──►│ Auth Check  │    │
│  │ /webhook    │    │ Signature   │    │
│  │ /billing    │    │ Validation  │    │
│  │ /invoices   │    │ Rate Limit  │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  Stripe     │    │ MercadoPago │    │
│  │  Handler    │    │   Handler   │    │
│  │             │    │             │    │
│  │ Payments    │    │ Payments    │    │
│  │ Webhooks    │    │ Webhooks    │    │
│  │ Customers   │    │ Preferences │    │
│  │ Invoices    │    │ Subscript.  │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Subscription│    │   Utils     │    │
│  │  Manager    │    │             │    │
│  │             │    │ Validators  │    │
│  │ Plans       │    │ Formatters  │    │
│  │ Billing     │    │ Encryption  │    │
│  │ Renewals    │    │ Logs        │    │
│  └─────────────┘    └─────────────┘    │
│         │                              │
│         ▼                              │
│  ┌─────────────────────────────────┐   │
│  │         DATABASE                │   │
│  │      MongoDB Atlas              │   │
│  │                                 │   │
│  │ Collections:                    │   │
│  │ - subscriptions                 │   │
│  │ - transactions                  │   │
│  │ - invoices                      │   │
│  │ - payment_methods              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Funcionalidades

### Core Features
- **Múltiples Pasarelas**: Stripe y Mercado Pago
- **Gestión de Suscripciones**: Planes Free, Premium, Enterprise
- **Procesamiento de Webhooks**: Eventos en tiempo real
- **Facturación**: Generación y gestión de facturas
- **Reportes**: Analytics de pagos y suscripciones
- **Reembolsos**: Procesamiento automatizado

### Endpoints Principales

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| POST | `/subscribe` | Crear nueva suscripción | ✅ |
| POST | `/stripe/webhook` | Webhook de Stripe | ❌ (Signature) |
| POST | `/mercadopago/webhook` | Webhook de MercadoPago | ❌ (Signature) |
| GET | `/subscription` | Estado de suscripción | ✅ |
| POST | `/cancel` | Cancelar suscripción | ✅ |
| GET | `/invoices` | Historial de facturas | ✅ |
| POST | `/payment-method` | Agregar método de pago | ✅ |

## 💰 Planes de Suscripción

### Plan Free
```python
class FreePlan:
    price = 0.00
    currency = "USD"
    interval = "month"
    features = {
        "chat_requests_per_hour": 50,
        "tokens_per_day": 10000,
        "available_llms": ["deepseek", "gemini"],
        "history_retention_days": 30,
        "export_formats": [],
        "priority_support": False
    }
```

### Plan Premium
```python
class PremiumPlan:
    price = 19.99
    currency = "USD"
    interval = "month"
    features = {
        "chat_requests_per_hour": 500,
        "tokens_per_day": 100000,
        "available_llms": ["openai", "claude", "deepseek", "gemini"],
        "history_retention_days": 365,
        "export_formats": ["pdf", "txt", "json"],
        "priority_support": True,
        "analytics": True
    }
```

### Plan Enterprise
```python
class EnterprisePlan:
    price = 99.99
    currency = "USD"
    interval = "month"
    features = {
        "chat_requests_per_hour": 5000,
        "tokens_per_day": 1000000,
        "available_llms": ["*"],
        "history_retention_days": "unlimited",
        "export_formats": ["*"],
        "priority_support": True,
        "analytics": True,
        "custom_models": True,
        "api_access": True,
        "dedicated_support": True
    }
```

## 📊 Modelos de Datos

### Subscription Model
```python
class Subscription(BaseModel):
    id: str
    user_id: str
    plan: str  # free, premium, enterprise
    status: str  # active, past_due, canceled, unpaid
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    stripe_subscription_id: Optional[str]
    mercadopago_subscription_id: Optional[str]
    payment_method: str  # stripe, mercadopago
    created_at: datetime
    updated_at: datetime
```

### Transaction Model
```python
class Transaction(BaseModel):
    id: str
    user_id: str
    subscription_id: str
    amount: float
    currency: str
    status: str  # pending, completed, failed, refunded
    payment_method: str
    provider_transaction_id: str
    created_at: datetime
    metadata: Dict[str, Any]
```

### Invoice Model
```python
class Invoice(BaseModel):
    id: str
    user_id: str
    subscription_id: str
    amount_due: float
    amount_paid: float
    currency: str
    status: str  # draft, open, paid, void, uncollectible
    due_date: datetime
    paid_at: Optional[datetime]
    invoice_pdf: Optional[str]
    line_items: List[LineItem]
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
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
SUBSCRIPTIONS_COLLECTION=subscriptions
TRANSACTIONS_COLLECTION=transactions
INVOICES_COLLECTION=invoices

# Business Logic
DEFAULT_TRIAL_DAYS=7
GRACE_PERIOD_DAYS=3
AUTO_RETRY_FAILED_PAYMENTS=true
SEND_EMAIL_NOTIFICATIONS=true
```

### Dependencias (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
stripe==7.8.0
mercadopago==2.2.1
pymongo==4.6.0
motor==3.3.2
httpx==0.26.0
cryptography==41.0.8
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
reportlab==4.0.7
jinja2==3.1.2
```

## 🎯 Integración con Stripe

### Customer Management
```python
import stripe

async def create_stripe_customer(user_email: str, user_name: str) -> str:
    """Crear customer en Stripe"""
    customer = stripe.Customer.create(
        email=user_email,
        name=user_name,
        metadata={"source": "llm_wrapper"}
    )
    return customer.id

async def create_subscription(customer_id: str, price_id: str) -> dict:
    """Crear suscripción en Stripe"""
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        trial_period_days=7,
        expand=["latest_invoice.payment_intent"]
    )
    return subscription
```

### Webhook Handling
```python
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Manejar webhooks de Stripe"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Procesar eventos
    if event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"])
    
    return {"status": "success"}
```

## 🌎 Integración con Mercado Pago

### Preference Creation
```python
import mercadopago

async def create_mercadopago_preference(
    user_id: str, 
    plan: str, 
    amount: float
) -> dict:
    """Crear preferencia de pago en MercadoPago"""
    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
    
    preference_data = {
        "items": [
            {
                "title": f"Suscripción {plan.title()}",
                "quantity": 1,
                "unit_price": amount,
                "currency_id": "USD"
            }
        ],
        "back_urls": {
            "success": "https://yourapp.com/payment/success",
            "failure": "https://yourapp.com/payment/failure",
            "pending": "https://yourapp.com/payment/pending"
        },
        "auto_return": "approved",
        "external_reference": user_id,
        "notification_url": "https://yourapp.com/mercadopago/webhook"
    }
    
    preference_response = sdk.preference().create(preference_data)
    return preference_response["response"]
```

## 🔔 Sistema de Webhooks

### Event Processing
```python
async def process_payment_event(
    provider: str, 
    event_type: str, 
    event_data: dict
):
    """Procesar eventos de pago de cualquier proveedor"""
    
    if event_type == "payment.succeeded":
        await activate_subscription(event_data["user_id"])
        await send_welcome_email(event_data["user_email"])
        await update_user_permissions(event_data["user_id"], event_data["plan"])
    
    elif event_type == "payment.failed":
        await handle_failed_payment(event_data["subscription_id"])
        await send_payment_retry_email(event_data["user_email"])
    
    elif event_type == "subscription.canceled":
        await deactivate_subscription(event_data["subscription_id"])
        await send_cancellation_email(event_data["user_email"])
```

## 📊 Reportes y Analytics

### Revenue Metrics
```python
async def get_revenue_metrics(start_date: datetime, end_date: datetime) -> dict:
    """Obtener métricas de ingresos"""
    return {
        "total_revenue": await calculate_total_revenue(start_date, end_date),
        "mrr": await calculate_mrr(),  # Monthly Recurring Revenue
        "arr": await calculate_arr(),  # Annual Recurring Revenue
        "churn_rate": await calculate_churn_rate(),
        "new_subscriptions": await count_new_subscriptions(start_date, end_date),
        "canceled_subscriptions": await count_canceled_subscriptions(start_date, end_date),
        "revenue_by_plan": await get_revenue_by_plan(start_date, end_date)
    }
```

## 🧪 Testing

### Unit Tests
```bash
# Test Stripe integration
pytest tests/test_stripe.py -v

# Test MercadoPago integration
pytest tests/test_mercadopago.py -v

# Test subscription logic
pytest tests/test_subscriptions.py -v

# Test webhooks
pytest tests/test_webhooks.py -v
```

### Mock Payments
```python
# Para testing sin cargos reales
STRIPE_TEST_CARDS = {
    "success": "4242424242424242",
    "declined": "4000000000000002",
    "insufficient_funds": "4000000000009995"
}
```

## 🚀 Desarrollo Local

### Setup Inicial
```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar servicio
uvicorn main:app --reload --port 8003
```

### Testing Webhooks Localmente
```bash
# Usar ngrok para exponer puerto local
ngrok http 8003

# Configurar webhook URLs en Stripe/MercadoPago dashboard
# con la URL de ngrok
```

## 🔒 Seguridad

### PCI Compliance
- No almacenamos datos de tarjetas de crédito
- Usamos tokens de Stripe/MercadoPago
- Validación de firmas en webhooks
- Encriptación de datos sensibles
- Logs auditables de transacciones

### Fraud Prevention
```python
async def validate_payment_request(request: PaymentRequest) -> bool:
    """Validar request de pago para prevenir fraude"""
    # Verificar límites de usuario
    # Validar patrones de gasto
    # Verificar geolocalización
    # Revisar historial de chargebacks
    return True
```

---

**Puerto**: 8003  
**Estado**: 🔄 En desarrollo  
**Próximo**: Implementar integración con Stripe 