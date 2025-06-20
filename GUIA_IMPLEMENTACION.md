# 🔧 Guía de Implementación - PI SDK WebPay

Esta guía te ayudará a integrar PI SDK WebPay en tu proyecto Django existente paso a paso.

## 📋 Tabla de Contenidos

- [🚀 Implementación Rápida](#-implementación-rápida)
- [📁 Estructura de Archivos](#-estructura-de-archivos)
- [⚙️ Configuración Detallada](#️-configuración-detallada)
- [🔗 Configuración de URLs](#-configuración-de-urls)
- [💾 Base de Datos](#-base-de-datos)
- [🧪 Verificación](#-verificación)
- [🔌 Uso en Tus Vistas](#-uso-en-tus-vistas)
- [🎨 Personalización](#-personalización)

---

## 🚀 Implementación Rápida

### Paso 1: Copiar la aplicación
```bash
# Desde el directorio de PI_SDK_WebPay
cp -r pagos/ /ruta/a/tu/proyecto/
# En Windows:
xcopy pagos "C:\ruta\a\tu\proyecto\pagos" /E /I
```

### Paso 2: Instalar dependencias
```bash
pip install transbank-sdk>=3.0.0
pip install requests>=2.28.0
```

### Paso 3: Configurar settings.py
```python
# En tu settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus apps existentes
    'mi_app',
    'otra_app',
    
    # ✅ Agregar PI SDK WebPay
    'pagos',
]

# ✅ Configuración Webpay
WEBPAY_PLUS_ENVIRONMENT = 'INTEGRATION'  # 'PRODUCTION' para producción
```

### Paso 4: Configurar URLs
```python
# En tu urls.py principal
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Tus URLs existentes
    path('mi-app/', include('mi_app.urls')),
    
    # ✅ URLs de WebPay
    path('pagos/', include('pagos.urls')),  # Con prefijo
    # O sin prefijo: path('', include('pagos.urls')),
]
```

### Paso 5: Migrar base de datos
```bash
python manage.py makemigrations pagos
python manage.py migrate
python manage.py crear_productos  # Opcional: crear productos de ejemplo
```

---

## 📁 Estructura de Archivos

Después de la integración, tu proyecto tendrá esta estructura:

```
tu_proyecto/
├── manage.py
├── tu_proyecto/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── mi_app/  # Tus apps existentes
├── pagos/   # ✅ App de WebPay integrada
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services_sdk.py
│   ├── utils.py
│   ├── admin.py
│   ├── templates/
│   │   └── pagos/
│   ├── static/
│   │   └── css/
│   └── management/
│       └── commands/
└── requirements.txt
```

---

## ⚙️ Configuración Detallada

### 1. Settings.py Completo

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Configuración básica
DEBUG = True
SECRET_KEY = 'tu-secret-key'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ✅ Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tus apps existentes
    'mi_app',
    
    # ✅ App de pagos WebPay
    'pagos',
]

# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ✅ Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Si tienes carpeta static global
]

# ✅ Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Si tienes templates globales
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ✅ Configuración específica WebPay
WEBPAY_PLUS_ENVIRONMENT = 'INTEGRATION'  # Para desarrollo
# Para producción cambiar a:
# WEBPAY_PLUS_ENVIRONMENT = 'PRODUCTION'
# WEBPAY_PLUS_COMMERCE_CODE = 'tu_codigo_comercio_real'
# WEBPAY_PLUS_API_KEY = 'tu_api_key_real'

# ✅ Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
```

### 2. Requirements.txt

Agregar a tu `requirements.txt`:
```txt
# Dependencias existentes...
Django>=4.2.0
transbank-sdk>=3.0.0
requests>=2.28.0
```

---

## 🔗 Configuración de URLs

### Opción 1: Con prefijo (Recomendado)

```python
# urls.py principal
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Tus URLs existentes
    path('', include('mi_app.urls')),  # Tu app principal
    path('blog/', include('blog.urls')),  # Otras apps
    
    # ✅ WebPay con prefijo
    path('pagos/', include('pagos.urls')),
]

# Resultado:
# - Tu app: http://127.0.0.1:8000/
# - WebPay: http://127.0.0.1:8000/pagos/
# - Dashboard: http://127.0.0.1:8000/pagos/vendedor/
```

### Opción 2: Sin prefijo

```python
# urls.py principal
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Tus URLs existentes CON prefijo
    path('mi-app/', include('mi_app.urls')),
    path('blog/', include('blog.urls')),
    
    # ✅ WebPay sin prefijo (página principal)
    path('', include('pagos.urls')),
]

# Resultado:
# - WebPay: http://127.0.0.1:8000/
# - Tu app: http://127.0.0.1:8000/mi-app/
# - Dashboard: http://127.0.0.1:8000/vendedor/
```

### Opción 3: Con prefijo personalizado

```python
# urls.py principal
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mi_app.urls')),
    
    # ✅ WebPay con prefijo personalizado
    path('tienda/', include('pagos.urls')),
    # O: path('webpay/', include('pagos.urls')),
    # O: path('checkout/', include('pagos.urls')),
]
```

---

## 💾 Base de Datos

### 1. Crear y aplicar migraciones

```bash
# Crear migraciones para la app pagos
python manage.py makemigrations pagos

# Aplicar todas las migraciones
python manage.py migrate

# Verificar migraciones aplicadas
python manage.py showmigrations
```

### 2. Crear datos de ejemplo

```bash
# Crear productos de ejemplo para probar
python manage.py crear_productos

# Crear superusuario para acceder al admin
python manage.py createsuperuser
```

### 3. Verificar modelos en admin

```python
# Si quieres personalizar el admin, edita pagos/admin.py
from django.contrib import admin
from .models import Producto, Transaccion, ItemCarrito

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['orden_compra', 'monto', 'estado', 'fecha']
    list_filter = ['estado', 'fecha']
    search_fields = ['orden_compra']
```

---

## 🧪 Verificación

### 1. Verificar configuración

```bash
# Verificar que no hay errores de configuración
python manage.py check

# Verificar específicamente la app pagos
python manage.py check pagos
```

### 2. Probar importaciones

```python
# En shell de Django
python manage.py shell

>>> from pagos.models import Producto, Transaccion
>>> from pagos.services_sdk import WebpaySDKService
>>> from pagos.utils import validar_session_key
>>> print("✅ Todas las importaciones funcionan")
```

### 3. Probar URLs

```bash
# Ejecutar servidor
python manage.py runserver

# Verificar URLs en el navegador:
# http://127.0.0.1:8000/pagos/  # (si usaste prefijo)
# http://127.0.0.1:8000/pagos/vendedor/
# http://127.0.0.1:8000/pagos/transacciones/
```

### 4. Probar APIs

```bash
# Probar API de transacciones
curl http://127.0.0.1:8000/pagos/transacciones/json/

# Probar API de dashboard
curl http://127.0.0.1:8000/pagos/vendedor/json/
```

---

## 🔌 Uso en Tus Vistas

### 1. Integrar pagos en tu checkout

```python
# En tu vista de checkout existente
from django.shortcuts import render, redirect
from pagos.services_sdk import WebpaySDKService
from pagos.utils import crear_transaccion_webpay

def mi_checkout_view(request):
    # Tu lógica existente del carrito
    items_carrito = obtener_items_carrito(request)
    total = calcular_total(items_carrito)
    
    if request.method == 'POST':
        # ✅ Crear transacción con WebPay
        try:
            resultado = crear_transaccion_webpay(
                request=request,
                monto=total,
                items_carrito=items_carrito
            )
            
            if resultado['success']:
                # Redirigir a WebPay
                return redirect(resultado['url'])
            else:
                messages.error(request, resultado['error'])
                
        except Exception as e:
            messages.error(request, f'Error al procesar pago: {str(e)}')
    
    return render(request, 'mi_app/checkout.html', {
        'items': items_carrito,
        'total': total
    })
```

### 2. Consultar transacciones desde tu app

```python
# En tu vista de historial de usuario
from pagos.models import Transaccion

def mi_historial_compras(request):
    # Si tienes usuarios logueados, puedes filtrar por usuario
    # (necesitarías modificar el modelo Transaccion para agregar usuario)
    
    transacciones = Transaccion.objects.filter(
        estado='EXITOSA',
        session_id=request.session.session_key
    ).order_by('-fecha')
    
    return render(request, 'mi_app/historial.html', {
        'transacciones': transacciones
    })
```

### 3. Usar el dashboard desde tu admin

```python
# En tu vista de administración
import requests
from django.http import JsonResponse

def obtener_estadisticas_ventas(request):
    """Vista para obtener datos del dashboard de WebPay"""
    try:
        # Llamar a la API interna
        response = requests.get('http://127.0.0.1:8000/pagos/vendedor/json/')
        data = response.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 🎨 Personalización

### 1. Personalizar templates

```bash
# Copiar templates para personalizar
mkdir -p templates/pagos
cp pagos/templates/pagos/* templates/pagos/

# Editar templates copiados
# templates/pagos/base.html
# templates/pagos/productos.html
# templates/pagos/carrito.html
```

### 2. Personalizar estilos CSS

```css
/* En tu static/css/custom.css */

/* Personalizar productos */
.producto-card {
    border: 2px solid #007bff;
    border-radius: 10px;
}

/* Personalizar carrito */
.carrito-item {
    background-color: #f8f9fa;
    padding: 15px;
    margin: 10px 0;
}

/* Personalizar dashboard */
.dashboard-stat {
    background: linear-gradient(45deg, #007bff, #0056b3);
    color: white;
    padding: 20px;
    border-radius: 8px;
}
```

### 3. Agregar tus propios productos

```python
# En tu management command o vista admin
from pagos.models import Producto

# Crear productos desde tu sistema existente
def migrar_mis_productos():
    mis_productos = MiProductoModel.objects.all()
    
    for producto in mis_productos:
        Producto.objects.create(
            nombre=producto.name,
            descripcion=producto.description,
            precio=producto.price,
            stock=producto.quantity,
            activo=producto.is_active
        )
```

### 4. Conectar con tu sistema de usuarios

```python
# Modificar pagos/models.py para agregar usuario
from django.contrib.auth.models import User

class Transaccion(models.Model):
    # Campos existentes...
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Agregar esta línea en las vistas donde se crea la transacción
    # transaccion.usuario = request.user if request.user.is_authenticated else None
```

---

## ✅ Checklist Final

- [ ] ✅ App `pagos` copiada a tu proyecto
- [ ] ✅ Dependencias instaladas (`transbank-sdk`, `requests`)
- [ ] ✅ `pagos` agregada a `INSTALLED_APPS`
- [ ] ✅ `WEBPAY_PLUS_ENVIRONMENT` configurado
- [ ] ✅ URLs configuradas en `urlpatterns`
- [ ] ✅ Migraciones aplicadas (`python manage.py migrate`)
- [ ] ✅ Productos de ejemplo creados
- [ ] ✅ Servidor ejecutándose sin errores
- [ ] ✅ URLs de WebPay funcionando
- [ ] ✅ APIs JSON respondiendo
- [ ] ✅ Dashboard de vendedor accesible
- [ ] ✅ Transacciones exitosas mostrándose

## 🎉 ¡Listo!

Tu proyecto ahora tiene integrado PI SDK WebPay. Puedes acceder a:

- **Tienda:** `http://127.0.0.1:8000/pagos/`
- **Dashboard:** `http://127.0.0.1:8000/pagos/vendedor/`
- **API Transacciones:** `http://127.0.0.1:8000/pagos/transacciones/json/`
- **API Dashboard:** `http://127.0.0.1:8000/pagos/vendedor/json/`

---

**¿Problemas?** Revisa que todas las dependencias estén instaladas y que las migraciones se hayan aplicado correctamente.
