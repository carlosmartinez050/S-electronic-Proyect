from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from shop.models import Categoria, Marca, Producto
from .models import DescuentoCategoria, DescuentoMarca, DescuentoProducto


class DescuentoCategoriaTestCase(TestCase):
    """Tests para el modelo DescuentoCategoria"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.categoria = Categoria.objects.create(
            nombre="Laptops",
            slug="laptops",
            descripcion="Laptops y computadoras portátiles"
        )
        
        self.descuento = DescuentoCategoria.objects.create(
            categoria=self.categoria,
            porcentaje=15.50,
            activo=True,
            descripcion="Descuento especial en laptops"
        )
    
    def test_creacion_descuento_categoria(self):
        """Verifica que se cree correctamente un descuento de categoría"""
        self.assertEqual(self.descuento.porcentaje, 15.50)
        self.assertTrue(self.descuento.activo)
        self.assertEqual(self.descuento.categoria, self.categoria)
    
    def test_descuento_categoria_string(self):
        """Verifica la representación en string del modelo"""
        # Decimal se convierte sin ceros finales: 15.50 → "15.5"
        self.assertIn(self.categoria.nombre, str(self.descuento))
        self.assertIn("Descuento", str(self.descuento))
        self.assertIn("%", str(self.descuento))
    
    def test_es_valido_activo_sin_fechas(self):
        """Un descuento activo sin límite de fechas debe ser válido"""
        self.assertTrue(self.descuento.es_valido())
    
    def test_es_valido_inactivo(self):
        """Un descuento inactivo no debe ser válido"""
        self.descuento.activo = False
        self.assertFalse(self.descuento.es_valido())
    
    def test_es_valido_fecha_inicio_futura(self):
        """Un descuento con fecha de inicio futura no debe ser válido"""
        self.descuento.fecha_inicio = timezone.now() + timedelta(days=1)
        self.assertFalse(self.descuento.es_valido())
    
    def test_es_valido_fecha_fin_pasada(self):
        """Un descuento con fecha de fin pasada no debe ser válido"""
        self.descuento.fecha_fin = timezone.now() - timedelta(days=1)
        self.assertFalse(self.descuento.es_valido())
    
    def test_es_valido_dentro_de_periodo_valido(self):
        """Un descuento dentro del período válido debe ser válido"""
        ahora = timezone.now()
        self.descuento.fecha_inicio = ahora - timedelta(days=1)
        self.descuento.fecha_fin = ahora + timedelta(days=1)
        self.assertTrue(self.descuento.es_valido())
    
    def test_clean_fecha_fin_invalida(self):
        """La validación clean debe rechazar fecha_fin <= fecha_inicio"""
        self.descuento.fecha_fin = self.descuento.fecha_inicio - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            self.descuento.clean()
    
    def test_clean_fecha_fin_igual_inicio(self):
        """La validación clean debe rechazar fecha_fin == fecha_inicio"""
        self.descuento.fecha_fin = self.descuento.fecha_inicio
        with self.assertRaises(ValidationError):
            self.descuento.clean()
    
    def test_clean_fecha_fin_valida(self):
        """La validación clean debe aceptar fecha_fin > fecha_inicio"""
        self.descuento.fecha_fin = self.descuento.fecha_inicio + timedelta(days=1)
        # No debe lanzar excepción
        try:
            self.descuento.clean()
        except ValidationError:
            self.fail("clean() lanzó ValidationError inesperado")
    
    def test_porcentaje_valido_0_100(self):
        """El porcentaje puede ser 0 o 100"""
        desc_0 = DescuentoCategoria.objects.create(
            categoria=Categoria.objects.create(
                nombre="Cat1",
                slug="cat1"
            ),
            porcentaje=0,
            activo=True
        )
        desc_100 = DescuentoCategoria.objects.create(
            categoria=Categoria.objects.create(
                nombre="Cat2",
                slug="cat2"
            ),
            porcentaje=100,
            activo=True
        )
        self.assertEqual(desc_0.porcentaje, 0)
        self.assertEqual(desc_100.porcentaje, 100)
    
    def test_meta_ordering(self):
        """Los descuentos deben estar ordenados por fecha de creación descendente"""
        descuento2 = DescuentoCategoria.objects.create(
            categoria=Categoria.objects.create(
                nombre="Tablets",
                slug="tablets",
                descripcion="Tablets"
            ),
            porcentaje=10,
            activo=True
        )
        
        descuentos = DescuentoCategoria.objects.all()
        self.assertEqual(descuentos[0].categoria.nombre, "Tablets")
        self.assertEqual(descuentos[1].categoria.nombre, "Laptops")


class DescuentoMarcaTestCase(TestCase):
    """Tests para el modelo DescuentoMarca"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.marca = Marca.objects.create(
            nombre="Samsung",
            slug="samsung",
            descripcion="Samsung Electronics"
        )
        
        self.descuento = DescuentoMarca.objects.create(
            marca=self.marca,
            porcentaje=20.00,
            activo=True,
            descripcion="Promoción Samsung"
        )
    
    def test_creacion_descuento_marca(self):
        """Verifica que se cree correctamente un descuento de marca"""
        self.assertEqual(self.descuento.porcentaje, 20.00)
        self.assertTrue(self.descuento.activo)
        self.assertEqual(self.descuento.marca, self.marca)
    
    def test_descuento_marca_string(self):
        """Verifica la representación en string del modelo"""
        # Decimal se convierte sin ceros finales: 20.00 → "20"
        self.assertIn(self.marca.nombre, str(self.descuento))
        self.assertIn("Descuento", str(self.descuento))
        self.assertIn("%", str(self.descuento))
    
    def test_es_valido_activo_sin_fechas(self):
        """Un descuento activo sin límite de fechas debe ser válido"""
        self.assertTrue(self.descuento.es_valido())
    
    def test_es_valido_inactivo(self):
        """Un descuento inactivo no debe ser válido"""
        self.descuento.activo = False
        self.assertFalse(self.descuento.es_valido())
    
    def test_es_valido_dentro_de_periodo_valido(self):
        """Un descuento dentro del período válido debe ser válido"""
        ahora = timezone.now()
        self.descuento.fecha_inicio = ahora - timedelta(days=5)
        self.descuento.fecha_fin = ahora + timedelta(days=5)
        self.assertTrue(self.descuento.es_valido())
    
    def test_clean_fecha_fin_invalida(self):
        """La validación clean debe rechazar fecha_fin <= fecha_inicio"""
        self.descuento.fecha_fin = self.descuento.fecha_inicio - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            self.descuento.clean()
    
    def test_porcentaje_valido_0(self):
        """El porcentaje 0 debe ser válido"""
        descuento = DescuentoMarca.objects.create(
            marca=self.marca,
            porcentaje=0,
            activo=True
        )
        self.assertEqual(descuento.porcentaje, 0)
    
    def test_porcentaje_valido_100(self):
        """El porcentaje 100 debe ser válido"""
        descuento = DescuentoMarca.objects.create(
            marca=self.marca,
            porcentaje=100,
            activo=True
        )
        self.assertEqual(descuento.porcentaje, 100)


class DescuentoProductoTestCase(TestCase):
    """Tests para el modelo DescuentoProducto"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.categoria = Categoria.objects.create(
            nombre="Smartphones",
            slug="smartphones",
            descripcion="Teléfonos inteligentes"
        )
        
        self.marca = Marca.objects.create(
            nombre="Apple",
            slug="apple",
            descripcion="Apple Inc."
        )
        
        self.producto = Producto.objects.create(
            nombre="iPhone 15 Pro",
            slug="iphone-15-pro",
            precio=1299.99,
            descripcion="Apple iPhone 15 Pro",
            categoria=self.categoria,
            marca=self.marca
        )
        
        self.descuento = DescuentoProducto.objects.create(
            producto=self.producto,
            porcentaje=10.00,
            activo=True,
            descripcion="Descuento especial iPhone 15 Pro"
        )
    
    def test_creacion_descuento_producto(self):
        """Verifica que se cree correctamente un descuento de producto"""
        self.assertEqual(self.descuento.porcentaje, 10.00)
        self.assertTrue(self.descuento.activo)
        self.assertEqual(self.descuento.producto, self.producto)
    
    def test_descuento_producto_string(self):
        """Verifica la representación en string del modelo"""
        # Decimal se convierte sin ceros finales: 10.00 → "10"
        self.assertIn(self.producto.nombre, str(self.descuento))
        self.assertIn("Descuento", str(self.descuento))
        self.assertIn("%", str(self.descuento))
    
    def test_es_valido_activo_sin_fechas(self):
        """Un descuento activo sin límite de fechas debe ser válido"""
        self.assertTrue(self.descuento.es_valido())
    
    def test_es_valido_fecha_inicio_pasada_sin_fin(self):
        """Un descuento con fecha inicio pasada y sin fin debe ser válido"""
        self.descuento.fecha_inicio = timezone.now() - timedelta(days=10)
        self.descuento.fecha_fin = None
        self.assertTrue(self.descuento.es_valido())
    
    def test_es_valido_inactivo(self):
        """Un descuento inactivo no debe ser válido"""
        self.descuento.activo = False
        self.assertFalse(self.descuento.es_valido())
    
    def test_es_valido_fecha_fin_igual_ahora(self):
        """Un descuento con fecha_fin igual a ahora no debe ser válido"""
        ahora = timezone.now()
        self.descuento.fecha_inicio = ahora - timedelta(days=1)
        self.descuento.fecha_fin = ahora
        self.assertFalse(self.descuento.es_valido())
    
    def test_clean_fecha_fin_invalida(self):
        """La validación clean debe rechazar fecha_fin <= fecha_inicio"""
        self.descuento.fecha_fin = self.descuento.fecha_inicio
        with self.assertRaises(ValidationError):
            self.descuento.clean()
    
    def test_porcentaje_decimales(self):
        """El porcentaje debe poder tener decimales"""
        descuento = DescuentoProducto.objects.create(
            producto=self.producto,
            porcentaje=33.33,
            activo=True
        )
        self.assertEqual(descuento.porcentaje, 33.33)
    
    def test_producto_debe_tener_marca(self):
        """El producto de un descuento debe tener marca asignada"""
        self.assertIsNotNone(self.producto.marca)
        self.assertEqual(self.producto.marca.nombre, "Apple")
        # Verificar que se puede acceder a través del descuento
        self.assertIsNotNone(self.descuento.producto.marca)
        self.assertEqual(self.descuento.producto.marca.nombre, "Apple")
    
    def test_producto_debe_tener_categoria(self):
        """El producto de un descuento debe tener categoría asignada"""
        self.assertIsNotNone(self.producto.categoria)
        self.assertEqual(self.producto.categoria.nombre, "Smartphones")
        # Verificar que se puede acceder a través del descuento
        self.assertIsNotNone(self.descuento.producto.categoria)
        self.assertEqual(self.descuento.producto.categoria.nombre, "Smartphones")
    
    def test_producto_sin_marca_no_puede_crearse(self):
        """Un producto sin marca no puede ser creado"""
        categoria = Categoria.objects.create(
            nombre="Monitores",
            slug="monitores",
            descripcion="Monitores"
        )
        
        with self.assertRaises(ValidationError):
            Producto.objects.create(
                nombre="Monitor 27 pulgadas",
                slug="monitor-27",
                precio=299.99,
                descripcion="Monitor gaming",
                categoria=categoria
                # Sin marca
            )
    
    def test_acceso_a_marca_categoria_desde_descuento(self):
        """Desde el descuento se puede acceder a marca y categoría del producto"""
        # Información de marca a través del descuento
        marca_nombre = self.descuento.producto.marca.nombre
        self.assertEqual(marca_nombre, "Apple")
        
        # Información de categoría a través del descuento
        categoria_nombre = self.descuento.producto.categoria.nombre
        self.assertEqual(categoria_nombre, "Smartphones")
        
        # El descuento hereda datos importantes
        self.assertTrue(self.descuento.producto.activo)
        self.assertGreater(self.descuento.producto.precio, 0)


class DescuentosIntegracionTestCase(TestCase):
    """Tests de integración entre los diferentes tipos de descuentos"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.categoria = Categoria.objects.create(
            nombre="Accesorios",
            slug="accesorios",
            descripcion="Accesorios de electrónica"
        )
        
        self.marca = Marca.objects.create(
            nombre="Anker",
            slug="anker",
            descripcion="Marca Anker"
        )
        
        self.producto = Producto.objects.create(
            nombre="Cargador USB-C",
            slug="cargador-usb-c",
            precio=29.99,
            descripcion="Cargador rápido USB-C",
            categoria=self.categoria,
            marca=self.marca
        )
    
    def test_crear_descuentos_multiples_tipos(self):
        """Se pueden crear descuentos de diferentes tipos para diferentes objetos"""
        desc_categoria = DescuentoCategoria.objects.create(
            categoria=self.categoria,
            porcentaje=5,
            activo=True
        )
        
        desc_marca = DescuentoMarca.objects.create(
            marca=self.marca,
            porcentaje=10,
            activo=True
        )
        
        desc_producto = DescuentoProducto.objects.create(
            producto=self.producto,
            porcentaje=15,
            activo=True
        )
        
        self.assertEqual(DescuentoCategoria.objects.count(), 1)
        self.assertEqual(DescuentoMarca.objects.count(), 1)
        self.assertEqual(DescuentoProducto.objects.count(), 1)
    
    def test_descuentos_independientes(self):
        """Cambios en un descuento no afectan a otros"""
        desc_categoria = DescuentoCategoria.objects.create(
            categoria=self.categoria,
            porcentaje=5,
            activo=True
        )
        
        desc_marca = DescuentoMarca.objects.create(
            marca=self.marca,
            porcentaje=10,
            activo=True
        )
        
        desc_categoria.activo = False
        desc_categoria.save()
        
        desc_marca_refrescado = DescuentoMarca.objects.get(pk=desc_marca.pk)
        self.assertTrue(desc_marca_refrescado.activo)
