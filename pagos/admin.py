from django.contrib import admin
from .models import Producto, ItemCarrito, Transaccion

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'activo')

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'producto', 'cantidad', 'subtotal', 'fecha_agregado')
    list_filter = ('fecha_agregado', 'producto')
    search_fields = ('session_key', 'producto__nombre')

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('orden_compra', 'monto', 'estado', 'authorization_code', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'payment_type_code')
    search_fields = ('orden_compra', 'session_id', 'authorization_code')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información básica', {
            'fields': ('orden_compra', 'session_id', 'token', 'monto', 'estado')
        }),
        ('Respuesta Webpay', {
            'fields': ('vci', 'authorization_code', 'response_code', 'transaction_date', 
                      'accounting_date', 'payment_type_code', 'installments_number')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )
