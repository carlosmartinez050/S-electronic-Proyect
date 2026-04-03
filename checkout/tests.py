from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from decimal import Decimal

from accounts.models import CustomUser
from shop.models import Categoria, Marca, Producto
from orders.models import Order, OrderItem
from shopping_cart.models import Carrito, ItemCarrito
from shopping_cart.cart import Carrito as CarritoHelper


class CheckoutTestBase(TestCase):
    """Clase base con helpers para los tests de checkout"""
    
    def add_product_to_cart(self, user, producto, cantidad=1):
        """Helper para agregar un producto al carrito del usuario"""
        carrito, _ = Carrito.objects.get_or_create(usuario=user)
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'precio_unitario': producto.precio
            }
        )
        if not created:
            item.cantidad = cantidad
            item.precio_unitario = producto.precio
            item.save()
        return carrito


class CheckoutViewAuthenticationTests(CheckoutTestBase):
    """Tests de autenticación para la vista de checkout"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
    def test_checkout_requires_login(self):
        """El checkout debe redirigir si no está autenticado"""
        response = self.client.get(self.checkout_url)
        
        # Debe redirigir a login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))
    
    def test_checkout_post_requires_login(self):
        """POST al checkout debe redirigir si no está autenticado"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))


class CheckoutViewEmptyCartTests(CheckoutTestBase):
    """Tests para checkout con carrito vacío"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
        # Crear usuario
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.client.login(username='test@example.com', password='password123')
    
    def test_empty_cart_redirects_to_home(self):
        """Carrito vacío debe redirigir a home"""
        response = self.client.get(self.checkout_url)
        
        # Debe redirigir a shop:home
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('shop:home'), response.url)
    
    def test_empty_cart_post_redirects_to_home(self):
        """POST con carrito vacío debe redirigir a home"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('shop:home'), response.url)


class CheckoutViewGetTests(CheckoutTestBase):
    """Tests para GET en checkout"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
        # Crear usuario
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.client.login(username='test@example.com', password='password123')
        
        # Crear categoría y producto
        self.categoria = Categoria.objects.create(
            nombre='Laptops',
            descripcion='Laptops gaming'
        )
        
        self.marca = Marca.objects.create(
            nombre='Dell',
            descripcion='Marca Dell'
        )
        
        self.producto = Producto.objects.create(
            nombre='Dell XPS 15',
            descripcion='Laptop gaming potente',
            categoria=self.categoria,
            marca=self.marca,
            precio=1500.00,
            stock=10
        )
    
    def test_checkout_get_with_items(self):
        """GET al checkout con items en carrito debe mostrar formulario"""
        # Agregar producto al carrito
        self.add_product_to_cart(self.user, self.producto, cantidad=2)
        
        # Hacer GET
        response = self.client.get(self.checkout_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')
        
        # Verificar contexto
        self.assertIn('carrito_items', response.context)
        self.assertIn('total_articulos', response.context)
        self.assertIn('subtotal', response.context)
        self.assertIn('total', response.context)
        
        # Verificar valores
        self.assertEqual(response.context['total_articulos'], 2)
        self.assertEqual(response.context['subtotal'], Decimal('3000.00'))
        self.assertEqual(response.context['total'], Decimal('3020.00'))  # + 20 de envío
    
    def test_checkout_context_includes_discount(self):
        """El contexto debe incluir campo de descuento"""
        self.add_product_to_cart(self.user, self.producto, cantidad=1)
        
        response = self.client.get(self.checkout_url)
        
        self.assertIn('descuento', response.context)


class CheckoutViewPostValidationTests(CheckoutTestBase):
    """Tests para validación de formulario en POST"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.client.login(username='test@example.com', password='password123')
        
        # Crear producto
        categoria = Categoria.objects.create(nombre='Laptops')
        marca = Marca.objects.create(nombre='Dell')
        self.producto = Producto.objects.create(
            nombre='Dell XPS 15',
            descripcion='Laptop',
            categoria=categoria,
            marca=marca,
            precio=1500.00,
            stock=10
        )
        
        # Agregar al carrito
        self.add_product_to_cart(self.user, self.producto, cantidad=1)
    
    def test_missing_nombre_validation(self):
        """Campo nombre vacío debe mostrar error"""
        response = self.client.post(self.checkout_url, {
            'nombre': '',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        self.assertEqual(response.status_code, 200)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Por favor completa todos los campos' in str(m) for m in messages_list))
    
    def test_missing_apellido_validation(self):
        """Campo apellido vacío debe mostrar error"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': '',
            'direccion': 'Calle 123'
        })
        
        self.assertEqual(response.status_code, 200)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Por favor completa todos los campos' in str(m) for m in messages_list))
    
    def test_missing_direccion_validation(self):
        """Campo dirección vacío debe mostrar error"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': ''
        })
        
        self.assertEqual(response.status_code, 200)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Por favor completa todos los campos' in str(m) for m in messages_list))
    
    def test_whitespace_only_validation(self):
        """Solo espacios en blanco debe ser considerado vacío"""
        response = self.client.post(self.checkout_url, {
            'nombre': '   ',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        self.assertEqual(response.status_code, 200)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Por favor completa todos los campos' in str(m) for m in messages_list))
    
    def test_validation_preserves_form_data(self):
        """Datos del formulario deben ser devueltos en caso de error"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': ''  # Falta la dirección
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form_data', response.context)
        self.assertEqual(response.context['form_data']['nombre'], 'Juan')
        self.assertEqual(response.context['form_data']['apellido'], 'Pérez')


class CheckoutViewPostSuccessTests(CheckoutTestBase):
    """Tests para creación exitosa de órdenes"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.client.login(username='test@example.com', password='password123')
        
        # Crear productos
        categoria = Categoria.objects.create(nombre='Laptops')
        marca = Marca.objects.create(nombre='Dell')
        
        self.producto1 = Producto.objects.create(
            nombre='Dell XPS 15',
            descripcion='Laptop',
            categoria=categoria,
            marca=marca,
            precio=1500.00,
            stock=10
        )
        
        self.producto2 = Producto.objects.create(
            nombre='Mouse Dell',
            descripcion='Mouse gaming',
            categoria=categoria,
            marca=marca,
            precio=50.00,
            stock=20
        )
        
        # Agregar múltiples items al carrito
        self.add_product_to_cart(self.user, self.producto1, cantidad=1)
        self.add_product_to_cart(self.user, self.producto2, cantidad=2)
    
    def test_successful_checkout_creates_order(self):
        """Checkout exitoso debe crear una Order"""
        initial_count = Order.objects.count()
        
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123 Apto 5'
        })
        
        # Debe haber una nueva orden
        self.assertEqual(Order.objects.count(), initial_count + 1)
        
        # Verificar que redirige a home
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('shop:home'), response.url)
    
    def test_order_has_correct_data(self):
        """La orden creada debe tener los datos correctos"""
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123 Apto 5'
        })
        
        order = Order.objects.last()
        
        self.assertEqual(order.usuario, self.user)
        self.assertEqual(order.nombre, 'Juan')
        self.assertEqual(order.apellido, 'Pérez')
        self.assertEqual(order.direccion, 'Calle 123 Apto 5')
        self.assertEqual(order.estado, Order.ESTADO_PENDIENTE)
    
    def test_order_totals_calculated_correctly(self):
        """Los totales de la orden deben calcularse correctamente"""
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        order = Order.objects.last()
        
        # Subtotal: 1500 * 1 + 50 * 2 = 1600
        self.assertEqual(order.subtotal, Decimal('1600.00'))
        self.assertEqual(order.costo_envio, Decimal('20.00'))
        self.assertEqual(order.total, Decimal('1620.00'))
    
    def test_order_items_created(self):
        """Cada producto del carrito debe crear un OrderItem"""
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        order = Order.objects.last()
        items = order.items.all()
        
        # Debe haber 2 items
        self.assertEqual(items.count(), 2)
    
    def test_order_item_data(self):
        """Cada OrderItem debe tener los datos correctos"""
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        order = Order.objects.last()
        item1 = order.items.get(producto=self.producto1)
        
        self.assertEqual(item1.nombre_producto, 'Dell XPS 15')
        self.assertEqual(item1.precio_unitario, Decimal('1500.00'))
        self.assertEqual(item1.cantidad, 1)
        self.assertEqual(item1.subtotal, Decimal('1500.00'))
    
    def test_cart_cleared_after_checkout(self):
        """El carrito debe vaciarse después del checkout"""
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        # Verificar carrito en BD está vacío
        carrito_db = Carrito.objects.get(usuario=self.user)
        self.assertEqual(carrito_db.items.count(), 0)
    
    def test_success_message_displayed(self):
        """Debe mostrarse mensaje de éxito"""
        response = self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        }, follow=True)
        
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Pedido recibido' in str(m) for m in messages_list))


class CheckoutOrderEdgeCasesTests(CheckoutTestBase):
    """Tests para casos especiales"""
    
    def setUp(self):
        self.client = Client()
        self.checkout_url = reverse('checkout:checkout')
        
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.client.login(username='test@example.com', password='password123')
        
        # Crear producto
        categoria = Categoria.objects.create(nombre='Laptops')
        marca = Marca.objects.create(nombre='Dell')
        self.producto = Producto.objects.create(
            nombre='Dell XPS 15',
            descripcion='Laptop',
            categoria=categoria,
            marca=marca,
            precio=1500.00,
            stock=10
        )
    
    def test_order_with_special_characters_in_address(self):
        """La dirección con caracteres especiales debe guardarse correctamente"""
        self.add_product_to_cart(self.user, self.producto, cantidad=1)
        
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle José María #123 Apto 5-B'
        })
        
        order = Order.objects.last()
        self.assertEqual(order.direccion, 'Calle José María #123 Apto 5-B')
    
    def test_preserves_product_price_at_purchase_time(self):
        """El precio guardado en OrderItem debe ser el del momento de compra"""
        self.add_product_to_cart(self.user, self.producto, cantidad=1)
        
        # Cambiar el precio del producto
        self.producto.precio = 2000.00
        self.producto.save()
        
        # Hacer checkout
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        order = Order.objects.last()
        item = order.items.first()
        
        # El precio guardado debe ser el original (1500), no el actual (2000)
        self.assertEqual(item.precio_unitario, Decimal('1500.00'))
    
    def test_order_preserves_user_relation(self):
        """La orden debe mantener relación con el usuario correcto"""
        self.add_product_to_cart(self.user, self.producto, cantidad=1)
        
        self.client.post(self.checkout_url, {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'direccion': 'Calle 123'
        })
        
        order = Order.objects.last()
        self.assertEqual(order.usuario, self.user)
        self.assertEqual(order.usuario.email, 'test@example.com')


