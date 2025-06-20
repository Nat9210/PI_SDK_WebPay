# 💳 PI SDK WebPay - Django + Transbank

Implementación completa de **Webpay Plus SDK de Transbank** para Django con dashboard de vendedor y APIs de transacciones.

## 🚀 Instalación

```bash
# 1. Clonar y configurar
git clone [URL_REPOSITORIO]
cd PI_SDK_WebPay
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configurar BD y datos
python manage.py migrate
python manage.py crear_productos

# 3. Ejecutar
python manage.py runserver
```

**Visita http://127.0.0.1:8000 para ver la tienda funcionando**

## ✨ Características Principales

- ✅ **Integración completa** con Webpay Plus SDK de Transbank
- ✅ **Dashboard de vendedor** con estadísticas en tiempo real
- ✅ **Transacciones exitosas** con historial detallado
- ✅ **APIs REST JSON** para consultas de datos
- ✅ **Sistema de pagos** funcional y seguro

## 🌐 URLs y APIs

### URLs Principales
| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000/` | Catálogo de productos |
| `http://127.0.0.1:8000/vendedor/` | **Dashboard de vendedor** |
| `http://127.0.0.1:8000/transacciones/` | **Transacciones exitosas** |

### APIs JSON
| Endpoint | Descripción | Parámetros |
|----------|-------------|------------|
| `/transacciones/json/` | **API Transacciones Exitosas** | `fecha_desde`, `fecha_hasta` |
| `/vendedor/json/` | **API Dashboard Vendedor** | `estado`, `fecha_desde`, `fecha_hasta` |

## 📊 Dashboard de Vendedor

**Acceso:** `http://127.0.0.1:8000/vendedor/`

### Funcionalidades:
- 📈 **Estadísticas de ventas** (día, semana, mes)
- 💰 **Ingresos totales y promedio**
- 📦 **Gestión de pedidos** por estado
- 🔍 **Filtros avanzados** por fecha y estado
- 📋 **Lista detallada** de todas las transacciones

### API JSON del Dashboard:
```bash
# Obtener todas las estadísticas
GET /vendedor/json/

# Filtrar por estado
GET /vendedor/json/?estado=PENDIENTE_REVISION

# Filtrar por fechas
GET /vendedor/json/?fecha_desde=2025-06-01&fecha_hasta=2025-06-30
```

## 📊 Transacciones Exitosas

**Acceso:** `http://127.0.0.1:8000/transacciones/`

### Funcionalidades:
- 📋 **Historial completo** de transacciones exitosas
- 🔍 **Filtros por fecha** y monto
- 📄 **Detalles de cada transacción**
- 💳 **Información de Webpay** (token, respuesta)

### API JSON de Transacciones:
```bash
# Obtener todas las transacciones exitosas
GET /transacciones/json/

# Filtrar por rango de fechas
GET /transacciones/json/?fecha_desde=2025-06-01&fecha_hasta=2025-06-30
```

## 🔌 Integración de Webpay

### Configuración básica:
```python
# pagos/services_sdk.py - Ya incluido en el proyecto
from transbank.webpay.webpay_plus.transaction import Transaction

class WebpaySDKService:
    def crear_transaccion(self, monto, orden_compra, session_id):
        transaction = Transaction()
        response = transaction.create(
            buy_order=orden_compra,
            session_id=session_id,
            amount=monto,
            return_url="http://127.0.0.1:8000/retorno/"
        )
        return response
```

### Flujo de pago:
1. **Usuario agrega productos** al carrito
2. **Presiona "Pagar"** → Se crea transacción en Webpay
3. **Redirección a Webpay** → Usuario paga con tarjeta
4. **Retorno a la tienda** → Se confirma o rechaza el pago
5. **Actualización automática** → Se registra en base de datos

## 🔧 Integración en Proyecto Existente

**📖 Para integración completa:** Ver [Guía de Implementación Detallada](GUIA_IMPLEMENTACION.md)

### Integración rápida:

### 1. Copiar la app:
```bash
cp -r pagos/ /ruta/a/tu/proyecto/
```

### 2. Configurar settings.py:
```python
INSTALLED_APPS = [
    # ... tus apps existentes
    'pagos',  # ← Agregar aquí
]

# Configuración Webpay
WEBPAY_PLUS_ENVIRONMENT = 'INTEGRATION'  # Para desarrollo
```

### 3. Configurar URLs:
```python
# urls.py principal
urlpatterns = [
    # ... tus URLs existentes
    path('', include('pagos.urls')),
]
```

### 4. Aplicar migraciones:
```bash
python manage.py migrate
python manage.py crear_productos
```

## 🛠️ Comandos Útiles

```bash
# Crear productos de ejemplo
python manage.py crear_productos

# Verificar configuración
python manage.py check

# Crear superusuario
python manage.py createsuperuser
```

## 📋 Requisitos

- Python 3.8+
- Django 4.2+
- Transbank SDK
- Credenciales Transbank (incluidas para desarrollo)

---

**Licencia:** MIT
