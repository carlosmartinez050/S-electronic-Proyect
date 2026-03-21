
# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from shop.models import Producto, Marca, Categoria

"""
Tests para AGREGAR productos al carrito
"""

class AgregarAlCarritoTest(TestCase):
    """Tests para la funcionalidad de agregar productos al carrito"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.client = Client()  # Cliente HTTP para hacer peticiones
        
        # Crear marca y categoría
        self.marca = Marca.objects.create(nombre="Samsung", activo=True)
        self.categoria = Categoria.objects.create(nombre="Smartphones", activo=True)
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre="Galaxy S23",
            marca=self.marca,
            categoria=self.categoria,
            precio=Decimal("18000.00"),
            stock=10,
            activo=True
        )
    
    def test_agregar_producto_al_carrito_primera_vez(self):
        """Verificar que se puede agregar un producto al carrito por primera vez"""
        url = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simular petición AJAX
        )
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Status 200 = OK
        
        # Verificar JSON
        data = response.json()
        self.assertTrue(data['success'])
        # assertTrue(X) → Verifica que X sea True
        
        self.assertEqual(data['total_articulos'], 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Debe haber 1 artículo en el carrito
        
        self.assertEqual(float(data['subtotal_producto']), 18000.00)
        # El subtotal debe ser el precio del producto
    
    def test_agregar_mismo_producto_incrementa_cantidad(self):
        """Verificar que agregar el mismo producto incrementa la cantidad"""
        url = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        
        # Agregar primera vez
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Agregar segunda vez
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Verificar que la cantidad es 2
        data = response.json()
        self.assertEqual(data['total_articulos'], 2)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertEqual(float(data['total_precio']), 36000.00)
        # Total = 18000 * 2 = 36000
    
    def test_agregar_producto_inexistente_falla(self):
        """Verificar que agregar un producto inexistente retorna 404"""
        url = reverse('cart:agregar_al_carrito', args=[99999])  # ID que no existe
        
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Debe retornar 404 (Not Found)
        self.assertEqual(response.status_code, 404)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
    
    def test_agregar_producto_actualiza_session(self):
        """Verificar que el carrito se guarda en la sesión"""
        url = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Verificar que la sesión tiene el carrito
        session = self.client.session
        self.assertIn('carrito', session)
        # assertIn(item, contenedor) → Verifica que 'item' ESTÁ en 'contenedor'
        
        self.assertEqual(session['carrito'][str(self.producto.id)], 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # La cantidad debe ser 1
    
    def test_agregar_dos_productos_diferentes(self):
        """Verificar que se pueden agregar diferentes productos"""
        # Crear segundo producto
        producto2 = Producto.objects.create(
            nombre="Galaxy S22",
            marca=self.marca,
            categoria=self.categoria,
            precio=Decimal("15000.00"),
            stock=5,
            activo=True
        )
        
        # Agregar primer producto
        url1 = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        self.client.post(url1, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Agregar segundo producto
        url2 = reverse('cart:agregar_al_carrito', args=[producto2.id])
        response = self.client.post(url2, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Verificar totales
        data = response.json()
        self.assertEqual(data['total_articulos'], 2)
        # 1 producto de cada uno = 2 artículos
        
        self.assertEqual(float(data['total_precio']), 33000.00)
        # 18000 + 15000 = 33000


# ============================================================================
# RESUMEN
# ============================================================================

"""
TESTS PARA AGREGAR PRODUCTOS (5 tests):

1. test_agregar_producto_al_carrito_primera_vez
   → Verifica que se puede agregar un producto nuevo

2. test_agregar_mismo_producto_incrementa_cantidad
   → Verifica que agregar el mismo producto suma la cantidad

3. test_agregar_producto_inexistente_falla
   → Verifica que productos inexistentes retornan 404

4. test_agregar_producto_actualiza_session
   → Verifica que la sesión se actualiza correctamente

5. test_agregar_dos_productos_diferentes
   → Verifica que se pueden tener varios productos en el carrito
"""


"""
Tests para ACTUALIZAR CANTIDAD de productos en el carrito
"""
class ActualizarCantidadTest(TestCase):
    """Tests para actualizar la cantidad de productos en el carrito"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.client = Client()
        
        marca = Marca.objects.create(nombre="Dell", activo=True)
        categoria = Categoria.objects.create(nombre="Laptops", activo=True)
        
        self.producto = Producto.objects.create(
            nombre="Dell Inspiron 15",
            marca=marca,
            categoria=categoria,
            precio=Decimal("10000.00"),
            stock=20,
            activo=True
        )
    
    def test_actualizar_cantidad_a_5(self):
        """Verificar que se puede actualizar la cantidad a 5"""
        url = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        
        # Primero agregar producto
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Actualizar cantidad a 5
        response = self.client.post(
            url,
            {'cantidad': 5},  # Enviar nueva cantidad
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        data = response.json()
        self.assertEqual(data['total_articulos'], 5)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # La cantidad debe ser 5
        
        self.assertEqual(float(data['total_precio']), 50000.00)
        # Total = 10000 * 5 = 50000
    
    def test_actualizar_cantidad_a_0_elimina_producto(self):
        """Verificar que actualizar a 0 elimina el producto"""
        url = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        
        # Agregar producto
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Actualizar a 0
        self.client.post(
            url,
            {'cantidad': 0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verificar que el carrito está vacío
        session = self.client.session
        self.assertNotIn(str(self.producto.id), session.get('carrito', {}))
        # assertNotIn(item, contenedor) → Verifica que 'item' NO está en 'contenedor'
        # El producto NO debe estar en el carrito
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA ACTUALIZAR CANTIDAD (2 tests):
 
1. test_actualizar_cantidad_a_5
   → Verifica que se puede cambiar la cantidad a un número específico
 
2. test_actualizar_cantidad_a_0_elimina_producto
   → Verifica que poner cantidad=0 elimina el producto del carrito
"""

"""
Tests para ELIMINAR productos del carrito
"""

class EliminarProductoTest(TestCase):
    """Tests para eliminar productos del carrito"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.client = Client()
        
        marca = Marca.objects.create(nombre="HP", activo=True)
        categoria = Categoria.objects.create(nombre="Laptops", activo=True)
        
        self.producto1 = Producto.objects.create(
            nombre="HP Pavilion",
            marca=marca,
            categoria=categoria,
            precio=Decimal("12000.00"),
            stock=10,
            activo=True
        )
        
        self.producto2 = Producto.objects.create(
            nombre="HP Envy",
            marca=marca,
            categoria=categoria,
            precio=Decimal("15000.00"),
            stock=5,
            activo=True
        )
    
    def test_eliminar_producto_del_carrito(self):
        """Verificar que se puede eliminar un producto"""
        # Agregar dos productos
        url1 = reverse('cart:agregar_al_carrito', args=[self.producto1.id])
        url2 = reverse('cart:agregar_al_carrito', args=[self.producto2.id])
        
        self.client.post(url1, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.client.post(url2, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Eliminar producto1
        url_eliminar = reverse('cart:eliminar_del_carrito', args=[self.producto1.id])
        response = self.client.post(url_eliminar, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        data = response.json()
        self.assertTrue(data['success'])
        # assertTrue(X) → Verifica que X sea True
        
        # Verificar que solo queda producto2 en la sesión
        session = self.client.session
        carrito = session.get('carrito', {})
        self.assertNotIn(str(self.producto1.id), carrito)
        # assertNotIn(item, contenedor) → Verifica que 'item' NO está en 'contenedor'
        
        self.assertIn(str(self.producto2.id), carrito)
        # assertIn(item, contenedor) → Verifica que 'item' ESTÁ en 'contenedor'
    
    def test_eliminar_ultimo_producto_vacia_carrito(self):
        """Verificar que eliminar el último producto deja el carrito vacío"""
        # Agregar un producto
        url = reverse('cart:agregar_al_carrito', args=[self.producto1.id])
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Eliminar el producto
        url_eliminar = reverse('cart:eliminar_del_carrito', args=[self.producto1.id])
        self.client.post(url_eliminar, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Verificar que el carrito está vacío
        session = self.client.session
        carrito = session.get('carrito', {})
        self.assertEqual(len(carrito), 0)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El carrito debe tener 0 productos
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA ELIMINAR PRODUCTOS (2 tests):
 
1. test_eliminar_producto_del_carrito
   → Verifica que se puede eliminar un producto específico
 
2. test_eliminar_ultimo_producto_vacia_carrito
   → Verifica que eliminar el último producto deja el carrito vacío
"""
 
 
"""
Tests para VISUALIZAR el carrito
"""
class VerCarritoTest(TestCase):
    """Tests para visualizar el carrito"""
    
    def setUp(self):
        """Crear datos de prueba"""
        self.client = Client()
        
        marca = Marca.objects.create(nombre="Lenovo", activo=True)
        categoria = Categoria.objects.create(nombre="Laptops", activo=True)
        
        self.producto = Producto.objects.create(
            nombre="Lenovo ThinkPad",
            marca=marca,
            categoria=categoria,
            precio=Decimal("16000.00"),
            stock=8,
            activo=True
        )
    
    def test_ver_carrito_vacio(self):
        """Verificar que se puede ver el carrito vacío"""
        url = reverse('cart:ver_carrito')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Status 200 = OK
        
        self.assertTrue(response.context['carrito_vacio'])
        # assertTrue(X) → Verifica que X sea True
        # El contexto debe indicar que está vacío
    
    def test_ver_carrito_con_productos(self):
        """Verificar que se pueden ver los productos en el carrito"""
        # Agregar producto
        url_agregar = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        self.client.post(url_agregar, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Ver carrito
        url_ver = reverse('cart:ver_carrito')
        response = self.client.get(url_ver)
        
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertFalse(response.context['carrito_vacio'])
        # assertFalse(X) → Verifica que X sea False
        # NO debe estar vacío
        
        self.assertEqual(len(response.context['lista_carrito']), 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Debe haber 1 producto en la lista
        
        self.assertEqual(response.context['total_articulos'], 1)
        # Total de artículos = 1
    
    def test_calcular_total_correctamente(self):
        """Verificar que el total se calcula correctamente"""
        # Agregar producto con cantidad 3
        url_agregar = reverse('cart:agregar_al_carrito', args=[self.producto.id])
        self.client.post(
            url_agregar,
            {'cantidad': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Ver carrito
        url_ver = reverse('cart:ver_carrito')
        response = self.client.get(url_ver)
        
        # Total debe ser 16000 * 3 = 48000
        self.assertEqual(response.context['total_precio'], Decimal("48000.00"))
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertEqual(response.context['total_articulos'], 3)
        # Total de artículos = 3
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA VISUALIZAR CARRITO (3 tests):
 
1. test_ver_carrito_vacio
   → Verifica que se puede ver el carrito vacío
 
2. test_ver_carrito_con_productos
   → Verifica que se muestran los productos correctamente
 
3. test_calcular_total_correctamente
   → Verifica que los totales se calculan bien
"""
 