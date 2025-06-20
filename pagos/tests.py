from django.test import TestCase, Client
from django.urls import reverse
from .models import Producto, Transaccion


class PagosViewsTestCase(TestCase):
    """Tests básicos para las vistas principales del sistema de pagos"""
    
    def setUp(self):
        self.client = Client()
        # Crear producto de prueba
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            precio=10000,
            descripcion="Producto para testing",
            stock=10
        )
    
    def test_productos_view(self):
        """Test que la vista de productos carga correctamente"""
        response = self.client.get(reverse('pagos:productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Producto Test')
    
    def test_carrito_view(self):
        """Test que la vista del carrito carga correctamente"""
        response = self.client.get(reverse('pagos:carrito'))
        self.assertEqual(response.status_code, 200)
    
    def test_agregar_carrito(self):
        """Test agregar producto al carrito"""
        response = self.client.post(
            reverse('pagos:agregar_carrito', args=[self.producto.id]),
            {'cantidad': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirect después de agregar


class ProductoModelTestCase(TestCase):
    """Tests para el modelo Producto"""
    
    def test_crear_producto(self):
        """Test crear producto"""
        producto = Producto.objects.create(
            nombre="Test Product",
            precio=5000,
            descripcion="Test Description",
            stock=5
        )
        self.assertEqual(producto.nombre, "Test Product")
        self.assertEqual(producto.precio, 5000)
        self.assertTrue(producto.activo)


class TransaccionModelTestCase(TestCase):
    """Tests para el modelo Transaccion"""
    
    def test_crear_transaccion(self):
        """Test crear transacción"""
        transaccion = Transaccion.objects.create(
            token="test_token_123",
            monto=15000,
            estado="AUTORIZADA",
            orden_compra="ORDER_TEST_001",
            session_id="test_session"
        )
        self.assertEqual(transaccion.estado, "AUTORIZADA")
        self.assertEqual(transaccion.monto, 15000)
