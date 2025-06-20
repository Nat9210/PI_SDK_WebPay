from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Producto, ItemCarrito, Transaccion
from .services_sdk import WebpaySDKService
from .utils import (
    validar_session_key,
    obtener_estadisticas_carrito,
    validar_datos_pago,
    agregar_producto_carrito,
    limpiar_carrito as limpiar_carrito_util,
    crear_transaccion_webpay,
    get_carrito_items,
    cambiar_estado_transaccion,
    procesar_filtros_fecha,
    procesar_filtros_transacciones,
    calcular_estadisticas_transacciones,
    preparar_detalle_productos_json,
    obtener_transacciones_autorizadas
)
import logging

logger = logging.getLogger(__name__)

# ===============================================
# VISTA 1: CATÁLOGO DE PRODUCTOS
# ===============================================
def productos(request):
    """Vista para mostrar todos los productos disponibles"""
    productos = Producto.objects.filter(activo=True)
    return render(request, 'pagos/productos.html', {'productos': productos})


def agregar_carrito(request, producto_id):
    """Agregar producto al carrito"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        session_key = validar_session_key(request)
        
        # Verificar stock
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles')
            return redirect('pagos:productos')
        
        # Verificar stock para item existente
        items_actuales = get_carrito_items(session_key).filter(producto=producto)
        if items_actuales.exists():
            cantidad_actual = items_actuales.first().cantidad
            if cantidad_actual + cantidad > producto.stock:
                messages.error(request, f'No hay suficiente stock. Máximo: {producto.stock}')
                return redirect('pagos:productos')
        
        # Agregar producto usando utilidad
        item, created = agregar_producto_carrito(session_key, producto, cantidad)
        messages.success(request, f'{producto.nombre} agregado al carrito')
    
    return redirect('pagos:productos')


def carrito(request):
    """Vista del carrito de compras"""
    session_key = validar_session_key(request)
    estadisticas = obtener_estadisticas_carrito(session_key)
    
    return render(request, 'pagos/carrito.html', {
        'productos_carrito': estadisticas['items'],
        'total': estadisticas['total_precio'],
    })


def limpiar_carrito(request):
    """Limpiar todos los productos del carrito"""
    session_key = request.session.session_key
    if session_key:
        limpiar_carrito_util(session_key)
        messages.success(request, 'Carrito limpiado exitosamente')
    return redirect('pagos:carrito')


def iniciar_pago(request):
    """Iniciar proceso de pago con Webpay"""
    if request.method == 'POST':
        session_key = validar_session_key(request)
        
        # Validar carrito usando utilidad
        es_valido, mensaje_error = validar_datos_pago(session_key)
        if not es_valido:
            messages.error(request, mensaje_error)
            return redirect('pagos:productos')
        
        # Obtener estadísticas del carrito
        estadisticas = obtener_estadisticas_carrito(session_key)
        total = estadisticas['total_precio']
        
        # Crear transacción usando utilidad
        transaccion = crear_transaccion_webpay(session_key, total)
        
        # Guardar detalle del carrito en la transacción
        transaccion.set_detalle_carrito(estadisticas['items'])
        transaccion.save()
        
        # URL de retorno
        url_retorno = request.build_absolute_uri(reverse('pagos:retorno_webpay'))
        
        # Crear transacción en Webpay
        webpay_service = WebpaySDKService()
        resultado = webpay_service.crear_transaccion(
            orden_compra=transaccion.orden_compra,
            session_id=transaccion.orden_compra,
            monto=total,
            url_retorno=url_retorno
        )
        
        if resultado['success']:
            # Guardar token
            transaccion.token = resultado['token']
            transaccion.save()
            
            # Guardar datos de transacción en sesión
            request.session['transaccion_id'] = transaccion.id
            
            # Redirigir a Webpay
            return render(request, 'pagos/redirect_webpay.html', {
                'url': resultado['url'],
                'token': resultado['token']
            })
        else:
            messages.error(request, f'Error al iniciar pago: {resultado["error"]}')
            return redirect('pagos:carrito')
    
    return redirect('pagos:carrito')


@csrf_exempt
def retorno_webpay(request):
    """Procesar retorno desde Webpay"""
    token_ws = request.POST.get('token_ws') or request.GET.get('token_ws')
    
    if not token_ws:
        messages.error(request, 'Token no recibido desde Webpay')
        return redirect('pagos:productos')
    
    try:
        # Buscar transacción por token
        transaccion = Transaccion.objects.get(token=token_ws)
          # Confirmar transacción con Webpay
        webpay_service = WebpaySDKService()
        resultado = webpay_service.confirmar_transaccion(token_ws)
        
        if resultado['success']:
            # Actualizar transacción con datos de respuesta
            transaccion.response_code = resultado.get('response_code')
            transaccion.payment_type_code = resultado.get('payment_type_code')
            transaccion.installments_number = resultado.get('installments_number')
            transaccion.vci = resultado.get('vci')
            transaccion.accounting_date = resultado.get('accounting_date')
            transaccion.transaction_date = resultado.get('transaction_date')
            transaccion.authorization_code = resultado.get('authorization_code')
            
            # Determinar estado según response_code
            if resultado.get('response_code') == 0:
                transaccion.estado = 'AUTORIZADA'
                
                # Limpiar carrito si el pago fue exitoso
                if hasattr(request, 'session') and request.session.session_key:
                    limpiar_carrito_util(request.session.session_key)
                
                messages.success(request, 'Pago realizado exitosamente')
            else:
                transaccion.estado = 'RECHAZADA'
                messages.error(request, 'El pago fue rechazado')
            
            transaccion.save()
            
            # Guardar ID de transacción en sesión para mostrar resultado
            request.session['transaccion_resultado_id'] = transaccion.id
            
        else:
            transaccion.estado = 'ERROR'
            transaccion.save()
            messages.error(request, f'Error al confirmar pago: {resultado["error"]}')
        
        return redirect('pagos:resultado')
        
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        return redirect('pagos:productos')
    except Exception as e:
        logger.error(f'Error en retorno_webpay: {str(e)}')
        messages.error(request, 'Error al procesar el pago')
        return redirect('pagos:productos')


def resultado(request):
    """Mostrar resultado del pago"""
    transaccion_id = request.session.get('transaccion_resultado_id')
    
    if not transaccion_id:
        messages.error(request, 'No hay información de transacción')
        return redirect('pagos:productos')
    
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)        # Limpiar la sesión
        if 'transaccion_resultado_id' in request.session:
            del request.session['transaccion_resultado_id']
        if 'transaccion_id' in request.session:
            del request.session['transaccion_id']
        
        return render(request, 'pagos/resultado.html', {
            'transaccion': transaccion,
            'exitoso': transaccion.estado == 'AUTORIZADA',
            'debug': True  # Solo para desarrollo
        })
        
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        return redirect('pagos:productos')


def vendedor_dashboard(request):
    """Dashboard simple del vendedor"""
    # Query base
    pedidos = obtener_transacciones_autorizadas()
    
    # Aplicar filtros usando función utilitaria
    pedidos = procesar_filtros_transacciones(pedidos, request)
      # Estadísticas básicas
    total_pedidos = pedidos.count()
    pedidos_pendientes = pedidos.filter(estado_pedido='PENDIENTE_REVISION').count()
    pedidos_aceptados = pedidos.filter(estado_pedido='ACEPTADO').count()
    pedidos_rechazados = pedidos.filter(estado_pedido='RECHAZADO').count()
    
    # Paginación simple (primeros 50)
    pedidos = pedidos[:50]
    
    return render(request, 'pagos/vendedor_dashboard.html', {
        'pedidos': pedidos,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_aceptados': pedidos_aceptados,
        'pedidos_rechazados': pedidos_rechazados,        'estado_filtro': request.GET.get('estado', ''),
        'busqueda': request.GET.get('busqueda', ''),
        'estados_opciones': [
            ('PENDIENTE_REVISION', 'Pendiente Revisión'),
            ('ACEPTADO', 'Aceptado'),
            ('RECHAZADO', 'Rechazado'),
            ('EN_PREPARACION', 'En Preparación'),
            ('ENVIADO', 'Enviado'),
            ('ENTREGADO', 'Entregado'),
        ]
    })


def vendedor_dashboard_json(request):
    """API JSON del dashboard vendedor - solo número de orden y detalle de compra"""
    # Obtener todas las transacciones autorizadas para el vendedor
    transacciones = obtener_transacciones_autorizadas()
    
    # Aplicar filtros usando función utilitaria
    transacciones = procesar_filtros_transacciones(transacciones, request)
    
    # Calcular estadísticas ANTES del slice
    estadisticas = {
        'total_pedidos': transacciones.count(),
        'pedidos_pendientes': transacciones.filter(estado_pedido='PENDIENTE_REVISION').count(),
        'pedidos_aceptados': transacciones.filter(estado_pedido='ACEPTADO').count(),
        'pedidos_rechazados': transacciones.filter(estado_pedido='RECHAZADO').count(),
    }
    
    # Limitar resultados para rendimiento
    transacciones = transacciones[:100]
    
    # Preparar datos para JSON - solo orden y detalle de compra
    data = []
    for transaccion in transacciones:        # Obtener detalle de la compra usando función utilitaria
        detalle_compra = preparar_detalle_productos_json(transaccion)
        
        data.append({
            'orden_compra': transaccion.orden_compra,
            'fecha': transaccion.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'monto_total': float(transaccion.monto),
            'estado_pedido': transaccion.estado_pedido,
            'estado_pedido_display': transaccion.get_estado_pedido_display(),
            'detalle_compra': detalle_compra
        })
    
    return JsonResponse({
        'estadisticas': estadisticas,
        'pedidos': data,
        'total': len(data)
    })


def vendedor_gestionar_estados(request, transaccion_id=None):
    """Gestionar estados de pedidos"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
    # Gestión individual
    if transaccion_id:
        accion = request.POST.get('accion')
        if not accion:
            messages.error(request, 'Acción no especificada')
            return redirect('pagos:vendedor_dashboard')
        
        transaccion = get_object_or_404(Transaccion, id=transaccion_id, estado='AUTORIZADA')
        
        # Usar utilidad para cambiar estado
        exito, mensaje = cambiar_estado_transaccion(transaccion, accion)
        
        if exito:
            messages.success(request, mensaje)
        else:
            messages.error(request, mensaje)
        
        return redirect('pagos:vendedor_dashboard')
    
    # Gestión en lote (básica)
    else:
        import json
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            pedido_ids = data.get('pedido_ids', [])
            
            if not accion or not pedido_ids:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Acción y pedidos son requeridos'
                }, status=400)
            
            # Estados válidos para lote
            estados_lote = {
                'aceptar': 'ACEPTADO',
                'rechazar': 'RECHAZADO',
                'cancelar': 'CANCELADO'
            }
            
            if accion not in estados_lote:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Acción "{accion}" no válida para operación en lote'
                }, status=400)
            
            # Actualizar pedidos en lote
            pedidos_actualizados = Transaccion.objects.filter(
                id__in=pedido_ids, 
                estado='AUTORIZADA'
            ).update(estado_pedido=estados_lote[accion])
            
            return JsonResponse({
                'status': 'success',
                'message': f'{pedidos_actualizados} pedidos actualizados exitosamente',
                'pedidos_actualizados': pedidos_actualizados
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            logger.error(f'Error en acciones lote: {str(e)}')
            return JsonResponse({'status': 'error', 'message': 'Error interno'}, status=500)


def transacciones_exitosas(request):
    """Vista de transacciones exitosas para el contador/visualización"""
    # Obtener todas las transacciones autorizadas
    transacciones = obtener_transacciones_autorizadas()
    
    # Aplicar filtros usando función utilitaria
    transacciones = procesar_filtros_transacciones(transacciones, request)
    
    # Calcular estadísticas usando función utilitaria
    estadisticas = calcular_estadisticas_transacciones(transacciones)
    
    # Limitar resultados para rendimiento
    transacciones = transacciones[:100]
    
    context = {
        'transacciones': transacciones,
        'total_transacciones': estadisticas['total_transacciones'],
        'monto_total': estadisticas['monto_total'],
        'monto_promedio': estadisticas['monto_promedio'],
        'estado_filtro': request.GET.get('estado_pedido', ''),
        'busqueda': request.GET.get('busqueda', ''),
        'fecha_desde': request.GET.get('fecha_desde', ''),
        'fecha_hasta': request.GET.get('fecha_hasta', ''),
        'estados_opciones': [
            ('PENDIENTE_REVISION', 'Pendiente Revisión'),
            ('ACEPTADO', 'Aceptado'),
            ('RECHAZADO', 'Rechazado'),
            ('EN_PREPARACION', 'En Preparación'),
            ('ENVIADO', 'Enviado'),
            ('ENTREGADO', 'Entregado'),
        ]
    }
    
    return render(request, 'pagos/transacciones_exitosas.html', context)


def transacciones_exitosas_json(request):
    """API JSON de transacciones exitosas para el contador"""
    # Obtener todas las transacciones autorizadas
    transacciones = obtener_transacciones_autorizadas()
    
    # Aplicar filtros usando función utilitaria
    transacciones = procesar_filtros_transacciones(transacciones, request)
    
    # Calcular estadísticas usando función utilitaria
    estadisticas = calcular_estadisticas_transacciones(transacciones)
    
    # Limitar resultados
    transacciones = transacciones[:100]
    
    # Preparar datos JSON
    datos_transacciones = []
    for t in transacciones:
        datos_transacciones.append({
            'id': t.id,
            'orden_compra': t.orden_compra,
            'monto': float(t.monto),
            'estado': t.estado,
            'estado_pedido': t.estado_pedido,
            'fecha_creacion': t.fecha_creacion.isoformat() if t.fecha_creacion else None,
            'authorization_code': t.authorization_code,
            'session_id': t.session_id,
            'productos': preparar_detalle_productos_json(t)
        })    
    respuesta = {
        'estadisticas': {
            'total_transacciones': estadisticas['total_transacciones'],
            'monto_total': float(estadisticas['monto_total']),
            'monto_promedio': float(estadisticas['monto_promedio'])
        },
        'transacciones': datos_transacciones,
        'filtros_aplicados': {
            'estado_pedido': request.GET.get('estado_pedido', ''),
            'fecha_desde': request.GET.get('fecha_desde', ''),
            'fecha_hasta': request.GET.get('fecha_hasta', '')
        }
    }
    
    return JsonResponse(respuesta)
