from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.productos, name='productos'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('limpiar-carrito/', views.limpiar_carrito, name='limpiar_carrito'),
    path('iniciar-pago/', views.iniciar_pago, name='iniciar_pago'),
    path('retorno/', views.retorno_webpay, name='retorno_webpay'),
    path('resultado/', views.resultado, name='resultado'),
    path('transacciones/', views.transacciones_exitosas, name='transacciones_exitosas'),
    path('transacciones/json/', views.transacciones_exitosas_json, name='transacciones_exitosas_json'),
    
    # URLs para vendedor
    path('vendedor/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('vendedor/json/', views.vendedor_dashboard_json, name='vendedor_dashboard_json'),
    path('vendedor/pedido/<int:transaccion_id>/gestionar/', views.vendedor_gestionar_estados, name='vendedor_gestionar_estados'),
    
    # URLs legacy para compatibilidad
    path('vendedor/pedido/<int:transaccion_id>/cambiar-estado/', views.vendedor_gestionar_estados, name='vendedor_cambiar_estado_pedido'),
    path('vendedor/pedido/<int:transaccion_id>/aceptar/', views.vendedor_gestionar_estados, name='vendedor_aceptar_pedido'),
    path('vendedor/pedido/<int:transaccion_id>/rechazar/', views.vendedor_gestionar_estados, name='vendedor_rechazar_pedido'),
]
