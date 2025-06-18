# API de Transacciones Exitosas - Documentación

## Descripción

Este módulo implementa una API JSON completa que muestra todos los detalles de las transacciones exitosas en el sistema de pagos con Webpay.

## Endpoints Disponibles

### 1. API JSON - Transacciones Exitosas
**URL:** `/api/transacciones-exitosas/`
**Método:** GET
**Descripción:** Retorna un JSON completo con todas las transacciones exitosas y sus detalles.

### 2. Vista Web - Transacciones Exitosas
**URL:** `/transacciones-exitosas/`
**Método:** GET
**Descripción:** Página web que muestra las transacciones exitosas en formato tabla con estadísticas.

## Estructura del JSON

```json
{
  "status": "success",
  "total_transacciones": 22,
  "fecha_consulta": "2025-06-18T10:34:16.123456-03:00",
  "transacciones": [
    {
      "id": 1,
      "orden_compra": "ORD-FF46A2357EA14E0A99D9",
      "detalles_basicos": {
        "monto": 49832.0,
        "estado": "AUTORIZADA",
        "fecha_creacion": "2025-06-18T10:34:16.123456-03:00",
        "fecha_actualizacion": "2025-06-18T10:34:16.123456-03:00",
        "session_id": "SES-123456789",
        "token": "TKN-abcdef123456..."
      },
      "detalle_carrito": {
        "productos": [
          {
            "producto_id": 1,
            "producto_nombre": "Laptop Gaming",
            "producto_precio": 25000.0,
            "cantidad": 2,
            "subtotal": 50000.0
          }
        ],
        "total_productos": 5,
        "resumen": {
          "cantidad_items": 3,
          "monto_total": 49832.0
        }
      },
      "detalles_webpay": {
        "vci": "TSY",
        "codigo_autorizacion": "123456",
        "codigo_respuesta": 0,
        "fecha_transaccion": "2025-06-18T10:34:16.123456-03:00",
        "fecha_contable": "0618",
        "tipo_pago": "VN",
        "numero_cuotas": 1
      },
      "informacion_adicional": {
        "metodo_pago": "Venta Normal",
        "estado_vci": "Autenticación exitosa",
        "resultado_transaccion": "Transacción aprobada"
      }
    }
  ],
  "estadisticas": {
    "monto_total": 5009496.0,
    "monto_promedio": 227704.36,
    "monto_maximo": 818833.0,
    "monto_minimo": 5127.0,
    "transacciones_por_tipo_pago": {
      "VN": {
        "cantidad": 8,
        "monto_total": 250000.0,
        "descripcion": "Venta Normal"
      }
    }
  }
}
```

## Características del JSON

### Datos Básicos de Transacción
- **ID**: Identificador único interno
- **Orden de Compra**: Código único de la transacción
- **Monto**: Valor de la transacción
- **Estado**: Estado actual (AUTORIZADA para exitosas)
- **Fechas**: Creación y última actualización
- **Session ID**: Identificador de sesión
- **Token**: Token de Webpay

### Detalles de Webpay
- **VCI**: Código de verificación del comercio
- **Código de Autorización**: Código único de autorización del banco
- **Código de Respuesta**: 0 = Exitosa
- **Fecha de Transacción**: Fecha real de procesamiento
- **Fecha Contable**: Fecha contable del banco en formato MMDD (ej: 0618 = 18 de Junio)
- **Tipo de Pago**: Tipo de transacción (VN, VD, VC, etc.)
- **Número de Cuotas**: Cantidad de cuotas si aplica

### Detalle del Carrito
- **Productos**: Lista completa de productos comprados
- **ID del Producto**: Identificador único del producto
- **Nombre del Producto**: Nombre descriptivo del producto
- **Precio Unitario**: Precio individual del producto
- **Cantidad**: Cantidad comprada
- **Subtotal**: Precio total por producto (precio × cantidad)
- **Total de Productos**: Suma total de todos los items
- **Resumen**: Información consolidada del carrito

### Información Adicional
- **Método de Pago**: Descripción legible del tipo de pago
- **Estado VCI**: Descripción del estado de verificación
- **Resultado**: Descripción del código de respuesta

### Estadísticas Generales
- **Monto Total**: Suma de todas las transacciones exitosas
- **Monto Promedio**: Promedio por transacción
- **Monto Máximo/Mínimo**: Valores extremos
- **Estadísticas por Tipo de Pago**: Agrupación por método de pago

## Formatos de Fecha

### Fecha Contable
La fecha contable de Webpay utiliza el formato **MMDD** (4 dígitos):
- **Formato**: MMDD
- **Ejemplo**: `0618` representa el 18 de Junio
- **Descripción**: Mes (2 dígitos) + Día (2 dígitos)
- **En la interfaz**: Se muestra como "18 de Junio" para mejor legibilidad

### Otras Fechas
- **Fecha de Transacción**: ISO 8601 completo (YYYY-MM-DDTHH:mm:ss)
- **Fecha de Creación**: ISO 8601 completo con zona horaria
- **Fecha de Actualización**: ISO 8601 completo con zona horaria

## Códigos de Referencia

### Códigos VCI
- **TSY**: Autenticación exitosa
- **TSN**: Autenticación fallida
- **TSU**: Autenticación no pudo ser realizada
- **TSA**: Intento de autenticación
- **TS**: Sin autenticación

### Tipos de Pago
- **VD**: Venta Débito
- **VN**: Venta Normal
- **VC**: Venta en Cuotas
- **SI**: Sin Interés
- **S2-S3**: Sin Interés 2-3 cuotas
- **N2-N12**: Cuotas con interés

### Códigos de Respuesta
- **0**: Transacción aprobada
- **-1**: Rechazo de transacción
- **-2**: Transacción debe reintentarse
- **-3**: Error en transacción
- **-4**: Rechazo de transacción
- **-5**: Rechazo por error de tasa
- **-6**: Excede cupo máximo mensual
- **-7**: Excede límite diario por transacción
- **-8**: Rubro no autorizado

## Comandos de Utilidad

### Crear Transacciones de Prueba
```bash
python manage.py crear_transacciones_prueba --cantidad 10
```

### Ejecutar Servidor
```bash
python manage.py runserver
```

## Acceso desde el Navegador

1. **Vista web**: http://127.0.0.1:8000/transacciones-exitosas/
2. **API JSON**: http://127.0.0.1:8000/api/transacciones-exitosas/

## 🔧 Integración

### Visualización del Token
- **En la tabla principal**: Vista previa truncada para mejor legibilidad
- **En detalles expandidos**: Token completo y funcional
- **Funcionalidad de copiado**: Clic en el token completo para copiarlo al portapapeles
- **Indicador visual**: Cambio de color al copiar exitosamente

### Consumir desde JavaScript
```javascript
fetch('/api/transacciones-exitosas/')
  .then(response => response.json())
  .then(data => {
    console.log('Total transacciones:', data.total_transacciones);
    console.log('Monto total:', data.estadisticas.monto_total);
    data.transacciones.forEach(transaccion => {
      console.log(`${transaccion.orden_compra}: $${transaccion.detalles_basicos.monto}`);
    });
  });
```

### Consumir desde Python
```python
import requests

response = requests.get('http://127.0.0.1:8000/api/transacciones-exitosas/')
data = response.json()

for transaccion in data['transacciones']:
    print(f"Orden: {transaccion['orden_compra']}")
    print(f"Monto: ${transaccion['detalles_basicos']['monto']}")
    print(f"Método: {transaccion['informacion_adicional']['metodo_pago']}")
    print("---")
```

## Interfaz Web

La vista web incluye:
- **Dashboard con estadísticas**: Resumen visual de las métricas principales con colores mejorados
- **Tabla interactiva**: Lista detallada con opción de expandir detalles
- **Columna de productos**: Muestra la cantidad de items comprados por transacción
- **Detalle del carrito**: Lista completa de productos comprados en cada transacción
- **Token completo**: El token de Webpay se muestra completo en los detalles expandibles
- **Funcionalidad de copiado**: Clic en el token para copiarlo al portapapeles
- **Vista previa en tabla**: Token truncado en la vista general, completo en detalles
- **Navegación integrada**: Acceso desde el menú principal
- **Enlace directo al JSON**: Botón para ver la API completa
- **Responsive design**: Compatible con dispositivos móviles
- **Mejoras de visibilidad**: Texto blanco corregido en tarjetas de estadísticas

---

**Desarrollado para:** Integración de Webpay SDK con Django
**Versión:** 1.0.0
**Fecha:** Junio 2025
