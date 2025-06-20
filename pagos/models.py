from django.db import models
import json


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Productos"


class ItemCarrito(models.Model):
    session_key = models.CharField(max_length=40)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"

    class Meta:
        unique_together = ('session_key', 'producto')


class Transaccion(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('AUTORIZADA', 'Autorizada'),
        ('RECHAZADA', 'Rechazada'),
        ('ANULADA', 'Anulada'),
    ]
    
    ESTADOS_PEDIDO = [
        ('PENDIENTE_REVISION', 'Pendiente de Revisión'),
        ('ACEPTADO', 'Aceptado por Vendedor'),
        ('RECHAZADO', 'Rechazado por Vendedor'),
        ('EN_PREPARACION', 'En Preparación'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
    ]

    orden_compra = models.CharField(max_length=26, unique=True)
    session_id = models.CharField(max_length=61)
    token = models.CharField(max_length=64, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    estado_pedido = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='PENDIENTE_REVISION')
    
    # Datos de respuesta de Webpay
    vci = models.CharField(max_length=10, blank=True)
    authorization_code = models.CharField(max_length=6, blank=True)
    response_code = models.IntegerField(blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    accounting_date = models.CharField(max_length=4, blank=True)
    payment_type_code = models.CharField(max_length=2, blank=True)
    installments_number = models.IntegerField(blank=True, null=True)
    
    # Detalle del carrito en JSON
    detalle_carrito = models.TextField(blank=True, help_text="JSON con los productos del carrito")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def get_detalle_carrito(self):
        """Retorna el detalle del carrito como objeto Python"""
        if self.detalle_carrito:
            try:
                return json.loads(self.detalle_carrito)
            except json.JSONDecodeError:
                return []
        return []

    def set_detalle_carrito(self, items_carrito):
        """Guarda los items del carrito en formato JSON"""
        carrito_data = [
            {
                'producto_id': item.producto.id,
                'producto_nombre': item.producto.nombre,
                'producto_precio': float(item.producto.precio),
                'cantidad': item.cantidad,
                'subtotal': float(item.subtotal)
            }
            for item in items_carrito
        ]
        self.detalle_carrito = json.dumps(carrito_data, ensure_ascii=False)

    def __str__(self):
        return f"Transacción {self.orden_compra} - {self.estado}"

    class Meta:
        verbose_name_plural = "Transacciones"
