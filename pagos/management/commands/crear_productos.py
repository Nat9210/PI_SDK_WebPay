from django.core.management.base import BaseCommand
from pagos.models import Producto

class Command(BaseCommand):
    help = 'Crear productos de prueba para la tienda'

    def handle(self, *args, **options):
        # Limpiar productos existentes
        Producto.objects.all().delete()
        
        productos = [
            {
                'nombre': 'Laptop Gaming',
                'descripcion': 'Laptop de alto rendimiento para gaming y trabajo profesional',
                'precio': 1299990,
                'stock': 5
            },
            {
                'nombre': 'Mouse Inalambrico',
                'descripcion': 'Mouse ergonomico con conexion Bluetooth',
                'precio': 29990,
                'stock': 20
            },
            {
                'nombre': 'Teclado Mecanico',
                'descripcion': 'Teclado mecanico retroiluminado para gaming',
                'precio': 89990,
                'stock': 15
            },
            {
                'nombre': 'Monitor 4K',
                'descripcion': 'Monitor 27 pulgadas con resolucion 4K UHD',
                'precio': 399990,
                'stock': 8
            },
            {
                'nombre': 'Auriculares Gaming',
                'descripcion': 'Auriculares con sonido surround 7.1 y microfono',
                'precio': 79990,
                'stock': 12
            }
        ]
        
        # Crear productos
        productos_creados = []
        for producto_data in productos:
            producto = Producto.objects.create(**producto_data)
            productos_creados.append(producto)
            self.stdout.write(f"Producto creado: {producto.nombre} - ${producto.precio}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Se han creado {len(productos_creados)} productos de prueba exitosamente.')
        )
