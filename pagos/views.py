from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
from .models import Producto, ItemCarrito, Transaccion
from .services_sdk import WebpaySDKService
import uuid
import logging

logger = logging.getLogger(__name__)

def productos(request):
    """Vista para mostrar todos los productos disponibles"""
    productos = Producto.objects.filter(activo=True)
    return render(request, 'pagos/productos.html', {'productos': productos})

def agregar_carrito(request, producto_id):
    """Agregar producto al carrito"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Asegurar que tenemos una sesión
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key
        
        # Verificar stock
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles')
            return redirect('pagos:productos')
        
        # Agregar o actualizar item en carrito
        item, created = ItemCarrito.objects.get_or_create(
            session_key=session_key,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            nueva_cantidad = item.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                messages.error(request, f'No hay suficiente stock. Máximo: {producto.stock}')
                return redirect('pagos:productos')
            item.cantidad = nueva_cantidad
            item.save()
        
        messages.success(request, f'{producto.nombre} agregado al carrito')
        return redirect('pagos:productos')
    
    return redirect('pagos:productos')

def carrito(request):
    """Vista del carrito de compras"""
    if not request.session.session_key:
        request.session.save()
    
    session_key = request.session.session_key
    productos_carrito = ItemCarrito.objects.filter(session_key=session_key)
    
    total = sum(item.subtotal for item in productos_carrito)
    
    context = {
        'productos_carrito': productos_carrito,
        'total': total,
    }
    return render(request, 'pagos/carrito.html', context)

def limpiar_carrito(request):
    """Limpiar todos los productos del carrito"""
    if request.session.session_key:
        ItemCarrito.objects.filter(session_key=request.session.session_key).delete()
        messages.success(request, 'Carrito limpiado exitosamente')
    return redirect('pagos:carrito')

def iniciar_pago(request):
    """Iniciar proceso de pago con Webpay"""
    if request.method == 'POST':
        if not request.session.session_key:
            messages.error(request, 'No hay productos en el carrito')
            return redirect('pagos:productos')
        
        session_key = request.session.session_key
        productos_carrito = ItemCarrito.objects.filter(session_key=session_key)
        
        if not productos_carrito.exists():
            messages.error(request, 'El carrito está vacío')
            return redirect('pagos:productos')
        
        # Calcular total
        total = sum(item.subtotal for item in productos_carrito)
        
        # Generar orden de compra única
        orden_compra = f"ORD-{uuid.uuid4().hex[:20].upper()}"
        session_id = f"SES-{uuid.uuid4().hex[:20].upper()}"
          # Crear transacción en BD
        transaccion = Transaccion.objects.create(
            orden_compra=orden_compra,
            session_id=session_id,
            monto=total
        )
        
        # Guardar detalle del carrito en la transacción
        transaccion.set_detalle_carrito(productos_carrito)
        transaccion.save()
        
        # URL de retorno
        url_retorno = request.build_absolute_uri(reverse('pagos:retorno_webpay'))
        
        # Crear transacción en Webpay
        webpay_service = WebpaySDKService()
        resultado = webpay_service.crear_transaccion(
            orden_compra=orden_compra,
            session_id=session_id,
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
            transaccion.vci = resultado.get('vci', '')
            transaccion.authorization_code = resultado.get('authorization_code', '')
            transaccion.response_code = resultado.get('response_code', -1)
            transaccion.transaction_date = resultado.get('transaction_date')
            transaccion.accounting_date = resultado.get('accounting_date', '')
            transaccion.payment_type_code = resultado.get('payment_type_code', '')
            transaccion.installments_number = resultado.get('installments_number', 0)
            
            # Determinar estado según response_code
            if resultado.get('response_code') == 0:
                transaccion.estado = 'AUTORIZADA'
                
                # Limpiar carrito si el pago fue exitoso
                if hasattr(request, 'session') and request.session.session_key:
                    ItemCarrito.objects.filter(session_key=request.session.session_key).delete()
                
                messages.success(request, 'Pago realizado exitosamente')
            else:
                transaccion.estado = 'RECHAZADA'
                messages.error(request, 'El pago fue rechazado')
            
            transaccion.save()
            
            # Guardar ID de transacción en sesión para mostrar resultado
            request.session['ultima_transaccion_id'] = transaccion.id
            
        else:
            transaccion.estado = 'RECHAZADA'
            transaccion.save()
            messages.error(request, f'Error al confirmar pago: {resultado["error"]}')
    
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
    except Exception as e:
        logger.error(f'Error en retorno Webpay: {str(e)}')
        messages.error(request, 'Error al procesar el retorno del pago')
    
    return redirect('pagos:resultado')

def resultado(request):
    """Mostrar resultado del pago"""
    transaccion_id = request.session.get('ultima_transaccion_id')
    
    if not transaccion_id:
        messages.error(request, 'No se encontró información de la transacción')
        return redirect('pagos:productos')
    
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)
        
        # Determinar el tipo de resultado basado en el estado de la transacción
        if transaccion.estado == 'AUTORIZADA':
            resultado = 'exitoso'
        elif transaccion.estado == 'RECHAZADA':
            resultado = 'fallido'
        elif transaccion.estado == 'PENDIENTE':
            resultado = 'proceso'
        else:
            resultado = 'error'
        
        context = {
            'transaccion': transaccion,
            'resultado': resultado
        }
        
        return render(request, 'pagos/resultado.html', context)
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        return redirect('pagos:productos')

def consultar_transaccion(request):
    """Consultar estado de una transacción"""
    transaccion = None
    
    if request.method == 'POST':
        orden_compra = request.POST.get('orden_compra')
        if orden_compra:
            try:
                transaccion = Transaccion.objects.get(orden_compra=orden_compra)
            except Transaccion.DoesNotExist:
                messages.error(request, 'Transacción no encontrada')
    
    return render(request, 'pagos/consultar_transaccion.html', {'transaccion': transaccion})

def transacciones_exitosas_json(request):
    """Vista que retorna un JSON con todas las transacciones exitosas y sus detalles"""
    try:
        # Obtener todas las transacciones autorizadas
        transacciones_exitosas = Transaccion.objects.filter(estado='AUTORIZADA').order_by('-fecha_creacion')
        
        # Construir el JSON con todos los detalles
        data = {
            'status': 'success',
            'total_transacciones': transacciones_exitosas.count(),
            'fecha_consulta': timezone.now().isoformat(),
            'transacciones': []
        }
        
        for transaccion in transacciones_exitosas:
            transaccion_data = {
                'id': transaccion.id,
                'orden_compra': transaccion.orden_compra,
                'detalles_basicos': {
                    'monto': float(transaccion.monto),
                    'estado': transaccion.estado,
                    'fecha_creacion': transaccion.fecha_creacion.isoformat(),
                    'fecha_actualizacion': transaccion.fecha_actualizacion.isoformat(),
                    'session_id': transaccion.session_id,
                    'token': transaccion.token
                },
                'detalle_carrito': {
                    'productos': transaccion.get_detalle_carrito(),
                    'total_productos': transaccion.get_total_productos(),
                    'resumen': {
                        'cantidad_items': len(transaccion.get_detalle_carrito()),
                        'monto_total': float(transaccion.monto)
                    }
                },
                'detalles_webpay': {
                    'vci': transaccion.vci,
                    'codigo_autorizacion': transaccion.authorization_code,
                    'codigo_respuesta': transaccion.response_code,
                    'fecha_transaccion': transaccion.transaction_date.isoformat() if transaccion.transaction_date else None,
                    'fecha_contable': transaccion.accounting_date,
                    'tipo_pago': transaccion.payment_type_code,
                    'numero_cuotas': transaccion.installments_number
                },
                'informacion_adicional': {
                    'metodo_pago': get_payment_method_description(transaccion.payment_type_code),
                    'estado_vci': get_vci_description(transaccion.vci),
                    'resultado_transaccion': get_response_code_description(transaccion.response_code)
                }
            }
            
            data['transacciones'].append(transaccion_data)
        
        # Agregar estadísticas generales
        if transacciones_exitosas:
            montos = [float(t.monto) for t in transacciones_exitosas]
            data['estadisticas'] = {
                'monto_total': sum(montos),
                'monto_promedio': sum(montos) / len(montos),
                'monto_maximo': max(montos),
                'monto_minimo': min(montos),
                'transacciones_por_tipo_pago': get_payment_stats(transacciones_exitosas)
            }
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f'Error al obtener transacciones exitosas: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Error interno del servidor',
            'detalle': str(e)
        }, status=500)

def get_payment_method_description(payment_type_code):
    """Obtiene la descripción del método de pago según el código"""
    payment_types = {
        'VD': 'Venta Débito',
        'VN': 'Venta Normal',
        'VC': 'Venta en Cuotas',
        'SI': 'Sin Interés',
        'S2': 'Sin Interés 2 cuotas',
        'S3': 'Sin Interés 3 cuotas',
        'N2': 'Cuotas 2',
        'N3': 'Cuotas 3',
        'N4': 'Cuotas 4',
        'N5': 'Cuotas 5',
        'N6': 'Cuotas 6',
        'N7': 'Cuotas 7',
        'N8': 'Cuotas 8',
        'N9': 'Cuotas 9',
        'N10': 'Cuotas 10',
        'N11': 'Cuotas 11',
        'N12': 'Cuotas 12'
    }
    return payment_types.get(payment_type_code, f'Código desconocido: {payment_type_code}')

def get_vci_description(vci):
    """Obtiene la descripción del VCI"""
    vci_codes = {
        'TSY': 'Autenticación exitosa',
        'TSN': 'Autenticación fallida',
        'TSU': 'Autenticación no pudo ser realizada',
        'TSA': 'Intento de autenticación',
        'TS': 'Sin autenticación',
        '': 'Sin información VCI'
    }
    return vci_codes.get(vci, f'VCI desconocido: {vci}')

def get_response_code_description(response_code):
    """Obtiene la descripción del código de respuesta"""
    if response_code == 0:
        return 'Transacción aprobada'
    elif response_code == -1:
        return 'Rechazo de transacción'
    elif response_code == -2:
        return 'Transacción debe reintentarse'
    elif response_code == -3:
        return 'Error en transacción'
    elif response_code == -4:
        return 'Rechazo de transacción'
    elif response_code == -5:
        return 'Rechazo por error de tasa'
    elif response_code == -6:
        return 'Excede cupo máximo mensual'
    elif response_code == -7:
        return 'Excede límite diario por transacción'
    elif response_code == -8:
        return 'Rubro no autorizado'
    else:
        return f'Código de respuesta: {response_code}'

def get_payment_stats(transacciones):
    """Obtiene estadísticas por tipo de pago"""
    stats = {}
    for transaccion in transacciones:
        tipo_pago = transaccion.payment_type_code or 'Sin especificar'
        if tipo_pago not in stats:
            stats[tipo_pago] = {
                'cantidad': 0,
                'monto_total': 0,
                'descripcion': get_payment_method_description(tipo_pago)
            }
        stats[tipo_pago]['cantidad'] += 1
        stats[tipo_pago]['monto_total'] += float(transaccion.monto)
    
    return stats

def transacciones_exitosas(request):
    """Vista para mostrar las transacciones exitosas en una página web"""
    transacciones_exitosas = Transaccion.objects.filter(estado='AUTORIZADA').order_by('-fecha_creacion')
    
    # Agregar formato legible de fecha contable a cada transacción
    for transaccion in transacciones_exitosas:
        transaccion.fecha_contable_legible = format_accounting_date_readable(transaccion.accounting_date)
    
    # Calcular estadísticas
    total_transacciones = transacciones_exitosas.count()
    monto_total = sum(t.monto for t in transacciones_exitosas)
    
    context = {
        'transacciones': transacciones_exitosas,
        'total_transacciones': total_transacciones,
        'monto_total': monto_total,
        'monto_promedio': monto_total / total_transacciones if total_transacciones > 0 else 0,
    }
    
    return render(request, 'pagos/transacciones_exitosas.html', context)

def format_accounting_date_readable(accounting_date):
    """Convierte fecha contable MMDD a formato legible"""
    if not accounting_date or len(accounting_date) != 4:
        return accounting_date or "-"
    
    try:
        month = int(accounting_date[:2])
        day = accounting_date[2:]
        
        months = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        month_name = months.get(month, 'Mes')
        return f"{day} de {month_name}"
    except:
        return accounting_date
