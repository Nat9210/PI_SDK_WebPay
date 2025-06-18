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
    path('consultar-transaccion/', views.consultar_transaccion, name='consultar_transaccion'),
    path('transacciones-exitosas/', views.transacciones_exitosas, name='transacciones_exitosas'),
    path('api/transacciones-exitosas/', views.transacciones_exitosas_json, name='transacciones_exitosas_json'),
]
