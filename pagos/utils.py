"""
Funciones auxiliares esenciales para el sistema de pagos Webpay
"""
import uuid
from datetime import datetime
from django.db.models import Q


# ======================================
# FUNCIONES PARA GESTIÓN DE CARRITO
# ======================================

def get_carrito_items(session_key):
    """Obtiene todos los items del carrito para una sesión"""
    from .models import ItemCarrito
    return ItemCarrito.objects.filter(session_key=session_key)


def calcular_total_carrito(session_key):
    """Calcula el total del carrito para una sesión"""
    items = get_carrito_items(session_key)
    return sum(item.producto.precio * item.cantidad for item in items)


def agregar_producto_carrito(session_key, producto, cantidad=1):
    """
    Agrega o actualiza un producto en el carrito
    Retorna (item, created) donde created indica si es nuevo
    """
    from .models import ItemCarrito
    
    item, created = ItemCarrito.objects.get_or_create(
        session_key=session_key,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        item.cantidad += cantidad
        item.save()
    
    return item, created


def limpiar_carrito(session_key):
    """Elimina todos los items del carrito para una sesión"""
    return get_carrito_items(session_key).delete()


def obtener_estadisticas_carrito(session_key):
    """Obtiene estadísticas del carrito (total items, total precio, etc.)"""
    items = get_carrito_items(session_key)
    total_items = sum(item.cantidad for item in items)
    total_precio = calcular_total_carrito(session_key)
    
    return {
        'items': items,
        'total_items': total_items,
        'total_precio': total_precio,
        'items_count': items.count()
    }


# ======================================
# FUNCIONES PARA GESTIÓN DE TRANSACCIONES
# ======================================

def crear_transaccion_webpay(session_key, monto):
    """Crea una nueva transacción para Webpay"""
    from .models import Transaccion
    import time
    import random
    
    # Generar orden de compra de máximo 26 caracteres
    # Formato: ORD + timestamp (10 dígitos) + random (4 dígitos) = 17 caracteres
    timestamp = str(int(time.time()))[-10:]  # Últimos 10 dígitos del timestamp
    random_suffix = str(random.randint(1000, 9999))
    orden_compra = f"ORD{timestamp}{random_suffix}"
    
    # Verificar que no exista (muy improbable, pero por seguridad)
    while Transaccion.objects.filter(orden_compra=orden_compra).exists():
        random_suffix = str(random.randint(1000, 9999))
        orden_compra = f"ORD{timestamp}{random_suffix}"
    
    return Transaccion.objects.create(
        orden_compra=orden_compra,
        session_id=session_key,
        monto=monto,
        estado='PENDIENTE'
    )


def cambiar_estado_transaccion(transaccion, nueva_accion):
    """
    Cambia el estado de una transacción basado en la acción
    Retorna (success, mensaje)
    """
    estados_map = {
        'aceptar': 'ACEPTADO',
        'rechazar': 'RECHAZADO',
        'preparacion': 'EN_PREPARACION',
        'enviado': 'ENVIADO',
        'entregado': 'ENTREGADO'
    }
    
    if nueva_accion not in estados_map:
        return False, f'Acción "{nueva_accion}" no válida'
    
    estado_anterior = transaccion.get_estado_pedido_display()
    transaccion.estado_pedido = estados_map[nueva_accion]
    transaccion.save()
    nuevo_estado = transaccion.get_estado_pedido_display()
    
    mensaje = f'Pedido {transaccion.orden_compra} cambiado de "{estado_anterior}" a "{nuevo_estado}"'
    return True, mensaje


def obtener_transacciones_autorizadas():
    """Obtiene todas las transacciones autorizadas ordenadas por fecha"""
    from .models import Transaccion
    return Transaccion.objects.filter(estado='AUTORIZADA').order_by('-fecha_creacion')


# ======================================
# FUNCIONES PARA VALIDACIÓN
# ======================================

def validar_datos_pago(session_key):
    """
    Valida que el carrito tenga productos y datos válidos para el pago
    Retorna (es_valido, mensaje_error)
    """
    items = get_carrito_items(session_key)
    
    if not items.exists():
        return False, "El carrito está vacío"
    
    total = calcular_total_carrito(session_key)
    if total <= 0:
        return False, "El total del carrito debe ser mayor a 0"
    
    # Verificar stock de productos
    for item in items:
        if not item.producto.activo:
            return False, f"El producto {item.producto.nombre} ya no está disponible"
    
    return True, ""


def validar_session_key(request):
    """Asegura que la request tenga una session_key válida"""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


# ======================================
# FUNCIONES PARA PROCESAMIENTO DE FILTROS
# ======================================

def procesar_filtros_fecha(queryset, fecha_desde, fecha_hasta):
    """
    Aplica filtros de fecha a un queryset de transacciones
    Retorna el queryset filtrado
    """
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    return queryset


def procesar_filtros_transacciones(transacciones, request):
    """
    Aplica todos los filtros comunes a las transacciones
    Retorna el queryset filtrado
    """
    estado_filtro = request.GET.get('estado', '') or request.GET.get('estado_pedido', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Filtro por estado
    if estado_filtro:
        transacciones = transacciones.filter(estado_pedido=estado_filtro)
    
    # Filtro por búsqueda
    if busqueda:
        from django.db.models import Q
        transacciones = transacciones.filter(
            Q(orden_compra__icontains=busqueda) |
            Q(authorization_code__icontains=busqueda)
        )
    
    # Filtros de fecha
    transacciones = procesar_filtros_fecha(transacciones, fecha_desde, fecha_hasta)
    
    return transacciones


def calcular_estadisticas_transacciones(transacciones):
    """
    Calcula estadísticas básicas de un conjunto de transacciones
    Retorna diccionario con estadísticas
    """
    total_transacciones = transacciones.count()
    monto_total = sum(t.monto for t in transacciones)
    monto_promedio = monto_total / total_transacciones if total_transacciones > 0 else 0
    
    return {
        'total_transacciones': total_transacciones,
        'monto_total': monto_total,
        'monto_promedio': monto_promedio
    }


def preparar_detalle_productos_json(transaccion):
    """
    Prepara el detalle de productos de una transacción para JSON
    Retorna lista de productos formateada
    """
    detalle = transaccion.get_detalle_carrito()
    productos_info = []
    
    for item in detalle:
        productos_info.append({
            'nombre': item['producto_nombre'],
            'cantidad': item['cantidad'],
            'precio': float(item['producto_precio']),
            'subtotal': float(item['subtotal'])
        })
    
    return productos_info