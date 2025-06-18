# 💳 Proyecto Webpay Plus SDK - Django

Implementación completa de integración con **Webpay Plus SDK de Transbank** para procesar pagos en línea con Django.

## 🚀 Características

- ✅ Integración completa con Webpay Plus SDK
- ✅ Sistema de carrito de compras
- ✅ API REST para consultar transacciones exitosas
- ✅ Vista web moderna para visualizar transacciones
- ✅ Sistema de productos básico
- ✅ Manejo de diferentes tipos de pago
- ✅ Dashboard con estadísticas detalladas

## 📦 Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd PI_SDK_WebPay

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
python manage.py migrate
python manage.py crear_productos

# 5. Ejecutar servidor
python manage.py runserver
```

## 🌐 URLs Principales

- **Productos**: http://127.0.0.1:8000/
- **Carrito**: http://127.0.0.1:8000/carrito/
- **Transacciones Exitosas**: http://127.0.0.1:8000/transacciones-exitosas/
- **API JSON**: http://127.0.0.1:8000/api/transacciones-exitosas/
- **Admin**: http://127.0.0.1:8000/admin/

## 📱 Ejemplo de API

```json
{
  "status": "success",
  "total_transacciones": 27,
  "fecha_consulta": "2025-06-18T15:44:12.301444+00:00",
  "transacciones": [
    {
      "id": 37,
      "orden_compra": "ORD-7B40585D885644C0BF48",
      "detalles_basicos": {
        "monto": 199970.0,
        "estado": "AUTORIZADA",
        "token": "01ab3781e7115e4792155a2bcc8615d0441f68b74818ec886cc4eadd73714567"
      },
      "detalle_carrito": {
        "productos": [
          {
            "producto_nombre": "Mouse Inalambrico",
            "producto_precio": 29990.0,
            "cantidad": 1,
            "subtotal": 29990.0
          }
        ]
      }
    }
  ],
  "estadisticas": {
    "monto_total": 10711638.0,
    "monto_promedio": 396727.33
  }
}
```

## 🛠️ Tecnologías

- **Backend**: Django 4.2+
- **Pagos**: Transbank SDK (Webpay Plus)
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, Bootstrap
- **API**: Django REST

## 📋 Funcionalidades

### 🛒 Sistema de Compras
- Catálogo de productos
- Carrito de compras
- Procesamiento de pagos con Webpay Plus
- Confirmación de transacciones

### 📊 Dashboard y Reportes
- Vista web de transacciones exitosas
- API REST para integraciones
- Estadísticas de ventas
- Filtros por tipo de pago

### 🔧 Administración
- Panel de administración Django
- Gestión de productos
- Seguimiento de transacciones

## 🔐 Configuración de Producción

Para usar en producción:

1. **Obtener credenciales reales de Transbank**
2. **Configurar variables de entorno**:
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=tu-dominio.com
   SECRET_KEY=tu-secret-key-segura
   ```
3. **Configurar base de datos PostgreSQL**
4. **Implementar HTTPS**
5. **Configurar servidor web (Nginx + Gunicorn)**

## 📁 Estructura del Proyecto

```
PI_SDK_WebPay/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── tienda_webpay_sdk/           # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── pagos/                       # Aplicación principal
    ├── models.py                # Modelos (Producto, Transaccion)
    ├── views.py                 # Vistas y API
    ├── services_sdk.py          # Integración Webpay SDK
    ├── urls.py                  # URLs de la app
    ├── templates/               # Plantillas HTML
    ├── static/                  # Archivos CSS/JS
    └── management/commands/     # Comandos personalizados
```

## 🔗 Integración en Proyectos Existentes

### Como Aplicación Django
```python
# En settings.py
INSTALLED_APPS = [
    # ... otras apps
    'pagos',
]

# En urls.py principal
urlpatterns = [
    path('pagos/', include('pagos.urls')),
]
```

### Como Microservicio
- Usar la API REST independientemente
- Comunicación HTTP entre servicios
- Escalabilidad independiente

## 📖 Documentación

- `DOCUMENTACION_COMPLETA.txt` - Manual técnico completo
- `INSTALACION_RAPIDA.txt` - Guía de instalación en 5 minutos
- `VERIFICACION_SISTEMA.txt` - Estado y funcionalidades

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Verificar configuración
python manage.py check

# Crear datos de prueba
python manage.py crear_productos
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🏆 Estado del Proyecto

✅ **Completamente funcional**  
✅ **Probado con 27+ transacciones**  
✅ **Listo para producción**  
✅ **Documentación completa**  

## 📞 Soporte

- 📧 Email: [tu-email@ejemplo.com]
- 🐛 Issues: [GitHub Issues]
- 📖 Docs: Ver archivos de documentación incluidos

---

**⚠️ Nota**: Este proyecto está configurado para ambiente de **INTEGRACIÓN (testing)** de Transbank. Para producción, obtén credenciales reales de Transbank.

**🎯 Desarrollado con**: Django + Webpay Plus SDK + ❤️
