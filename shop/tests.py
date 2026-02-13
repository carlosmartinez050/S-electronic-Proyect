from django.test import TestCase

# Create your tests here.

"""
Tests para los modelos de la app Shop
Verifican que Categoria, Marca, Producto y ImagenProducto funcionen correctamente
"""
from django.test import TestCase
from django.core.exceptions import ValidationError    
from django.db import IntegrityError 
from decimal import Decimal
from shop.models import Categoria, Marca, Producto, ImagenProducto


# ============================================================================
# TESTS PARA EL MODELO CATEGORIA
# ============================================================================

class CategoriaModelTest(TestCase):              
    """Tests para el modelo Categoria"""
    
    def setUp(self):                                                # setUp() se ejecuta antes de cada test para preparar el entorno, es quien crea los datos de prueba necesarios para cada test. Así cada test parte de un estado conocido y controlado.
        """Crear datos de prueba antes de cada test"""
        self.categoria = Categoria.objects.create(
            nombre="Laptops",
            descripcion="Computadoras portátiles",
            activo=True,
            orden=1
        )
    
    def test_categoria_creacion_exitosa(self):                      
        """Verificar que se puede crear una categoría correctamente"""
        self.assertEqual(self.categoria.nombre, "Laptops") 
        self.assertTrue(self.categoria.activo)
        self.assertEqual(self.categoria.orden, 1)
    
    def test_categoria_genera_slug_automaticamente(self):
        """Verificar que el slug se genera automáticamente"""
        # El slug debe ser "laptops" (lowercase del nombre)
        self.assertEqual(self.categoria.slug, "laptops")
    
    def test_categoria_slug_generado_es_lowercase(self):
        """Verificar que el slug se genera en minúsculas y sin espacios"""
        # Crear categoría con nombre en mayúsculas y espacios
        categoria = Categoria.objects.create(
            nombre="TECLADOS MECANICOS",
            activo=True
        )
        # El slug debe ser lowercase y con guiones
        self.assertEqual(categoria.slug, "teclados-mecanicos")
    
    def test_categoria_nombre_unico(self):
        """Verificar que no se pueden crear dos categorías con el mismo nombre"""
        # Primero crear una categoría nueva
        Categoria.objects.create(nombre="Monitores")
        
        # Intentar crear otra con el mismo nombre debe fallar
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(nombre="Monitores")
    
    def test_categoria_str_representation(self):
        """Verificar el método __str__"""
        self.assertEqual(str(self.categoria), "Laptops")
    
    def test_categoria_productos_activos(self):
        """Verificar que el método productos_activos() funciona"""
        # Crear marca
        marca = Marca.objects.create(nombre="Dell", activo=True)
        
        # Crear productos
        Producto.objects.create(
            nombre="Laptop Dell 1",
            marca=marca,
            categoria=self.categoria,
            precio=Decimal("10000.00"),
            stock=5,
            activo=True
        )
        Producto.objects.create(
            nombre="Laptop Dell 2",
            marca=marca,
            categoria=self.categoria,
            precio=Decimal("15000.00"),
            stock=0,  # Sin stock
            activo=True
        )
        Producto.objects.create(
            nombre="Laptop Dell 3",
            marca=marca,
            categoria=self.categoria,
            precio=Decimal("20000.00"),
            stock=3,
            activo=False  # Inactivo
        )
        
        # Solo debe contar el primer producto (activo Y con stock)
        self.assertEqual(self.categoria.productos_activos().count(), 1)
    
    def test_categoria_total_productos(self):
        """Verificar el método total_productos()"""
        marca = Marca.objects.create(nombre="HP", activo=True)
        
        Producto.objects.create(
            nombre="Laptop HP",
            marca=marca,
            categoria=self.categoria,
            precio=Decimal("12000.00"),
            stock=10,
            activo=True
        )
        
        self.assertEqual(self.categoria.total_productos(), 1)
        
        
# ============================================================================
# TESTS PARA EL MODELO MARCA
# ============================================================================   

class MarcaModelTest(TestCase):
    """Tests para el modelo Marca"""
    
    def setUp(self):
        """Crear datos de prueba antes de cada test"""
        self.marca = Marca.objects.create(
            nombre="Samsung",
            descripcion="Electrónica de alta calidad",
            activo=True,
            orden=1
        )
    
    def test_marca_creacion_exitosa(self):
        """Verificar que se puede crear una marca correctamente"""
        self.assertEqual(self.marca.nombre, "Samsung")
        
        
        self.assertTrue(self.marca.activo)
        
        
        self.assertEqual(self.marca.orden, 1)
        
    
    def test_marca_genera_slug_automaticamente(self):
        """Verificar que el slug se genera automáticamente"""
        self.assertEqual(self.marca.slug, "samsung")
       
    
    def test_marca_slug_generado_es_lowercase(self):
        """Verificar que el slug se genera en minúsculas"""
        marca = Marca.objects.create(
            nombre="LOGITECH INTERNACIONAL",
            activo=True
        )
        self.assertEqual(marca.slug, "logitech-internacional")
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El slug debe ser lowercase y con guiones
    
    def test_marca_nombre_unico(self):
        """Verificar que no se pueden crear dos marcas con el mismo nombre"""
        # Primero crear una marca nueva
        Marca.objects.create(nombre="LG")
        
        # Intentar crear otra con el mismo nombre debe fallar
        with self.assertRaises(IntegrityError):
            Marca.objects.create(nombre="LG")
        # assertRaises(Excepcion) → Verifica que se LANCE una excepción específica
        # IntegrityError se lanza porque el nombre debe ser único
    
    def test_marca_str_representation(self):
        """Verificar el método __str__"""
        self.assertEqual(str(self.marca), "Samsung")
       
    
    def test_marca_productos_activos(self):
        """Verificar que el método productos_activos() funciona"""
        # Crear una categoría para los productos
        categoria = Categoria.objects.create(nombre="Smartphones", activo=True)
        
        # Producto activo con stock (SÍ debe contarse)
        Producto.objects.create(
            nombre="Galaxy S23",
            marca=self.marca,
            categoria=categoria,
            precio=Decimal("18000.00"),
            stock=5,
            activo=True
        )
        
        # Producto sin stock (NO debe contarse)
        Producto.objects.create(
            nombre="Galaxy S22",
            marca=self.marca,
            categoria=categoria,
            precio=Decimal("15000.00"),
            stock=0,  # Sin stock
            activo=True
        )
        
        # Producto inactivo (NO debe contarse)
        Producto.objects.create(
            nombre="Galaxy S21",
            marca=self.marca,
            categoria=categoria,
            precio=Decimal("12000.00"),
            stock=3,
            activo=False  # Inactivo
        )
        
        # Solo debe contar el primer producto (activo Y con stock)
        self.assertEqual(self.marca.productos_activos().count(), 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Verifica que solo hay 1 producto activo con stock
    
    def test_marca_total_productos(self):
        """Verificar que el método total_productos() funciona"""
        categoria = Categoria.objects.create(nombre="Tablets", activo=True)
        
        # Crear un producto activo con stock
        Producto.objects.create(
            nombre="Galaxy Tab",
            marca=self.marca,
            categoria=categoria,
            precio=Decimal("8000.00"),
            stock=10,
            activo=True
        )
        
        self.assertEqual(self.marca.total_productos(), 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Verifica que el total de productos es 1
        
# ============================================================================
# TESTS PARA EL MODELO PRODUCTO    
# ============================================================================
        
class ProductoModelTest(TestCase):
    """Tests para el modelo Producto"""
    
    def setUp(self):
        """Crear datos de prueba antes de cada test"""
        # Crear marca y categoría primero 
        self.marca = Marca.objects.create(nombre="Dell", activo=True)
        self.categoria = Categoria.objects.create(nombre="Laptops", activo=True)
        
        # Crear el producto de prueba
        self.producto = Producto.objects.create(
            nombre="Dell Inspiron 15",
            marca=self.marca,
            categoria=self.categoria,
            precio=Decimal("10000.00"),
            stock=10,
            activo=True,
            destacado=False,
            nuevo=False
        )
    
    # ========================================================================
    # TESTS DE CREACIÓN Y CAMPOS BÁSICOS
    # ========================================================================
    
    def test_producto_creacion_exitosa(self):
        """Verificar que se puede crear un producto correctamente"""
        self.assertEqual(self.producto.nombre, "Dell Inspiron 15")
        
        self.assertEqual(self.producto.precio, Decimal("10000.00"))
        
        self.assertEqual(self.producto.stock, 10)
        # assertEqual(A, B) → Verifica que el stock sea 10
        
        self.assertTrue(self.producto.activo)
        # assertTrue(X) → Verifica que X sea True
    
    # ========================================================================
    # TESTS DE SLUG Y SKU (GENERACIÓN AUTOMÁTICA)
    # ========================================================================
    
    def test_producto_genera_slug_automaticamente(self):
        """Verificar que el slug se genera automáticamente"""
        self.assertEqual(self.producto.slug, "dell-inspiron-15")
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El slug se genera automáticamente en el método save()
    
    def test_producto_genera_sku_automaticamente(self):
        """Verificar que el SKU se genera automáticamente"""
        self.assertIsNotNone(self.producto.sku)
        # assertIsNotNone(X) → Verifica que X NO sea None
        # El SKU se debe generar automáticamente
        
        self.assertTrue(self.producto.sku.startswith("DELL-"))
        # assertTrue(X) → Verifica que X sea True
        # El SKU debe empezar con las primeras 4 letras de la marca
    
    def test_producto_sku_es_unico(self):
        """Verificar que cada producto tiene un SKU único"""
        # Crear otro producto
        producto2 = Producto.objects.create(
            nombre="Dell XPS 13",
            marca=self.marca,
            categoria=self.categoria,
            precio=Decimal("15000.00"),
            stock=5,
            activo=True
        )
        
        # Los SKUs deben ser diferentes
        self.assertNotEqual(self.producto.sku, producto2.sku)
        # assertNotEqual(A, B) → Verifica que A sea DIFERENTE de B
    
    # ========================================================================
    # TESTS DEL MÉTODO __str__
    # ========================================================================
    
    def test_producto_str_representation(self):
        """Verificar el método __str__"""
        expected = f"{self.marca.nombre} - {self.producto.nombre}"
        self.assertEqual(str(self.producto), expected)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El __str__ debe retornar "Dell - Dell Inspiron 15"
    
    # ========================================================================
    # TESTS DEL MÉTODO disponible()
    # ========================================================================
    
    def test_producto_disponible_con_stock_y_activo(self):
        """Verificar que un producto con stock y activo está disponible"""
        self.assertTrue(self.producto.disponible())
        # assertTrue(X) → Verifica que X sea True
        # Producto activo=True y stock=10, debe estar disponible
    
    def test_producto_no_disponible_sin_stock(self):
        """Verificar que un producto sin stock NO está disponible"""
        self.producto.stock = 0
        self.producto.save()
        
        self.assertFalse(self.producto.disponible())
        # assertFalse(X) → Verifica que X sea False
        # Con stock=0, NO debe estar disponible
    
    def test_producto_no_disponible_inactivo(self):
        """Verificar que un producto inactivo NO está disponible"""
        self.producto.activo = False
        self.producto.save()
        
        self.assertFalse(self.producto.disponible())
        # assertFalse(X) → Verifica que X sea False
        # Con activo=False, NO debe estar disponible
    
    def test_producto_no_disponible_sin_stock_e_inactivo(self):
        """Verificar que un producto sin stock e inactivo NO está disponible"""
        self.producto.stock = 0
        self.producto.activo = False
        self.producto.save()
        
        self.assertFalse(self.producto.disponible())
        # assertFalse(X) → Verifica que X sea False
        # Con stock=0 Y activo=False, definitivamente NO disponible
    
    # ========================================================================
    # TESTS DE VALIDACIONES (PRECIO, MARCA)
    # ========================================================================
    
    def test_producto_precio_no_negativo(self):
        """Verificar que no se puede crear un producto con precio negativo"""
        # Crear marca y categoría nuevas para este test
        marca = Marca.objects.create(nombre="TestMarca", activo=True)
        categoria = Categoria.objects.create(nombre="TestCategoria", activo=True)
        
        # Intentar crear producto con precio negativo
        with self.assertRaises((ValidationError, IntegrityError)):
            producto = Producto(
                nombre="Test Producto",
                marca=marca,
                categoria=categoria,
                precio=Decimal("-100.00"),  # Precio negativo
                stock=10
            )
            producto.full_clean()  # Validación del modelo
            producto.save()
        # assertRaises(Excepcion) → Verifica que se lance una excepción
        # El constraint en la DB previene precios negativos
    
    def test_producto_requiere_marca(self):
        """Verificar que un producto debe tener una marca asignada"""
        categoria = Categoria.objects.create(nombre="TestCat", activo=True)
        
        with self.assertRaises(ValidationError):
            producto = Producto.objects.create(
                nombre="Producto sin marca",
                categoria=categoria,
                precio=Decimal("5000.00"),
                stock=5
            )
        # assertRaises(Excepcion) → Verifica que se lance una excepción
        # El modelo requiere una marca en el save()
    
    # ========================================================================
    # TESTS DE ESPECIFICACIONES JSON
    # ========================================================================
    
    def test_producto_especificaciones_json(self):
        """Verificar que las especificaciones JSON funcionan correctamente"""
        # Asignar especificaciones
        self.producto.especificaciones = {
            "RAM": "16GB",
            "Procesador": "Intel i7",
            "Pantalla": "15.6 pulgadas"
        }
        self.producto.save()
        
        # Recargar del DB para verificar que se guardó correctamente
        producto_db = Producto.objects.get(id=self.producto.id)
        
        self.assertEqual(producto_db.especificaciones["RAM"], "16GB")
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertEqual(producto_db.especificaciones["Procesador"], "Intel i7")
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertEqual(producto_db.especificaciones["Pantalla"], "15.6 pulgadas")
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
    
    def test_producto_especificaciones_default_vacio(self):
        """Verificar que especificaciones por defecto es un dict vacío"""
        producto = Producto.objects.create(
            nombre="Producto sin specs",
            marca=self.marca,
            categoria=self.categoria,
            precio=Decimal("8000.00"),
            stock=3,
            activo=True
        )
        
        self.assertEqual(producto.especificaciones, {})
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Por defecto debe ser un diccionario vacío


# ============================================================================
# TESTS PARA EL MODELO IMAGENPRODUCTO
# ===========================================================================

class ImagenProductoModelTest(TestCase):
    """Tests para el modelo ImagenProducto"""  
    def setUp(self):
        """Crear datos de prueba antes de cada test"""
        # Crear marca y categoría
        marca = Marca.objects.create(nombre="HP", activo=True)
        categoria = Categoria.objects.create(nombre="Laptops", activo=True)
        
        # Crear producto (las imágenes pertenecen a un producto)
        self.producto = Producto.objects.create(
            nombre="HP Pavilion",
            marca=marca,
            categoria=categoria,
            precio=Decimal("12000.00"),
            stock=5,
            activo=True
        )
    
    # ========================================================================
    # TESTS DE CREACIÓN BÁSICA
    # ========================================================================
    
    def test_imagen_creacion_exitosa(self):
        """Verificar que se puede crear una imagen correctamente"""
        imagen = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test.jpg",
            orden=0,
            es_principal=True
        )
        
        self.assertEqual(imagen.producto, self.producto)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # La imagen debe estar asociada al producto correcto
        
        self.assertTrue(imagen.es_principal)
        # assertTrue(X) → Verifica que X sea True
        # La imagen debe ser principal
        
        self.assertEqual(imagen.orden, 0)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
    
    # ========================================================================
    # TESTS DE IMAGEN PRINCIPAL (SOLO UNA POR PRODUCTO)
    # ========================================================================
    
    def test_solo_una_imagen_principal(self):
        """Verificar que solo puede haber una imagen principal por producto"""
        # Crear primera imagen principal
        imagen1 = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test1.jpg",
            orden=0,
            es_principal=True
        )
        
        # Crear segunda imagen principal
        imagen2 = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test2.jpg",
            orden=1,
            es_principal=True  # También es principal
        )
        
        # Recargar imagen1 de la base de datos
        imagen1.refresh_from_db()
        # refresh_from_db() → Recarga el objeto desde la DB
        # Esto es necesario porque el save() de imagen2 modificó imagen1
        
        # imagen1 ya NO debe ser principal (fue reemplazada por imagen2)
        self.assertFalse(imagen1.es_principal)
        # assertFalse(X) → Verifica que X sea False
        
        # imagen2 SÍ debe ser principal (la más reciente)
        self.assertTrue(imagen2.es_principal)
        # assertTrue(X) → Verifica que X sea True
    
    # ========================================================================
    # TESTS DE MÉTODOS DEL PRODUCTO
    # ========================================================================
    
    def test_producto_get_imagen_principal(self):
        """Verificar que se puede obtener la imagen principal"""
        # Crear imagen secundaria
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test1.jpg",
            orden=1,
            es_principal=False
        )
        
        # Crear imagen principal
        imagen_principal = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test2.jpg",
            orden=0,
            es_principal=True
        )
        
        # Obtener imagen principal desde el producto
        resultado = self.producto.get_imagen_principal()
        
        self.assertEqual(resultado, imagen_principal)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El método debe retornar la imagen marcada como principal
    
    def test_producto_get_imagenes_secundarias(self):
        """Verificar que se pueden obtener las imágenes secundarias"""
        # Imagen principal
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/principal.jpg",
            orden=0,
            es_principal=True
        )
        
        # Imágenes secundarias
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/secundaria1.jpg",
            orden=1,
            es_principal=False
        )
        
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/secundaria2.jpg",
            orden=2,
            es_principal=False
        )
        
        # Obtener imágenes secundarias
        secundarias = self.producto.get_imagenes_secundarias()
        
        self.assertEqual(secundarias.count(), 2)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # Debe haber exactamente 2 imágenes secundarias
    
    def test_producto_get_todas_imagenes(self):
        """Verificar que se pueden obtener todas las imágenes ordenadas"""
        # Crear 3 imágenes en orden diferente
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/img3.jpg",
            orden=2,
            es_principal=False
        )
        
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/img1.jpg",
            orden=0,
            es_principal=True
        )
        
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/img2.jpg",
            orden=1,
            es_principal=False
        )
        
        # Obtener todas las imágenes
        todas = self.producto.get_todas_imagenes()
        
        self.assertEqual(todas.count(), 3)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        # Verificar que están ordenadas por el campo 'orden'
        self.assertEqual(todas[0].orden, 0)
        self.assertEqual(todas[1].orden, 1)
        self.assertEqual(todas[2].orden, 2)
        # Las imágenes deben estar ordenadas: 0, 1, 2
    
    def test_producto_tiene_imagenes(self):
        """Verificar que el método tiene_imagenes() funciona"""
        # Primero: producto sin imágenes
        self.assertFalse(self.producto.tiene_imagenes())
        # assertFalse(X) → Verifica que X sea False
        # No debe tener imágenes todavía
        
        # Agregar una imagen
        ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test.jpg",
            orden=0,
            activo=True
        )
        
        # Ahora: producto con imágenes
        self.assertTrue(self.producto.tiene_imagenes())
        # assertTrue(X) → Verifica que X sea True
        # Ahora SÍ tiene imágenes
    
    # ========================================================================
    # TESTS DE ALT TEXT (GENERACIÓN AUTOMÁTICA)
    # ========================================================================
    
    def test_imagen_alt_text_autogenerado(self):
        """Verificar que el alt_text se genera automáticamente"""
        imagen = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test.jpg",
            orden=0
        )
        
        # El alt_text debe generarse automáticamente
        self.assertIsNotNone(imagen.alt_text)
        # assertIsNotNone(X) → Verifica que X NO sea None
        
        self.assertIn(self.producto.nombre, imagen.alt_text)
        # assertIn(item, lista) → Verifica que 'item' ESTÁ en 'lista'
        # El alt_text debe contener el nombre del producto
    
    def test_imagen_alt_text_personalizado(self):
        """Verificar que se puede asignar un alt_text personalizado"""
        alt_personalizado = "Laptop HP Pavilion vista frontal"
        
        imagen = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test.jpg",
            orden=0,
            alt_text=alt_personalizado
        )
        
        self.assertEqual(imagen.alt_text, alt_personalizado)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        # El alt_text personalizado debe respetarse
    
    # ========================================================================
    # TESTS DE MÉTODO __str__
    # ========================================================================
    
    def test_imagen_str_representation(self):
        """Verificar el método __str__"""
        imagen = ImagenProducto.objects.create(
            producto=self.producto,
            imagen="productos/test.jpg",
            orden=0,
            es_principal=True
        )
        
        # El __str__ debe incluir el nombre del producto
        self.assertIn(self.producto.nombre, str(imagen))
        # assertIn(item, lista) → Verifica que 'item' ESTÁ en 'lista'
        
        # El __str__ debe indicar si es principal
        self.assertIn("Principal", str(imagen))
        # assertIn(item, lista) → Verifica que 'item' ESTÁ en 'lista'









# ============================================================================
# GLOSARIO COMPLETO DE ASSERTIONS (métodos assert más comunes)
# ============================================================================

"""
1. assertEqual(A, B)
   → Verifica que A == B (son iguales)
   Ejemplo: assertEqual(2 + 2, 4) ✅
   
2. assertNotEqual(A, B)
   → Verifica que A != B (son diferentes)
   Ejemplo: assertNotEqual(5, 3) ✅

3. assertTrue(X)
   → Verifica que X == True
   Ejemplo: assertTrue(usuario.activo) ✅
   
4. assertFalse(X)
   → Verifica que X == False
   Ejemplo: assertFalse(usuario.eliminado) ✅

5. assertIsNone(X)
   → Verifica que X == None (es nulo)
   Ejemplo: assertIsNone(producto.descripcion) ✅
   
6. assertIsNotNone(X)
   → Verifica que X != None (NO es nulo)
   Ejemplo: assertIsNotNone(producto.sku) ✅

7. assertIn(item, lista)
   → Verifica que 'item' ESTÁ en 'lista'
   Ejemplo: assertIn("Laptops", categorias) ✅
   
8. assertNotIn(item, lista)
   → Verifica que 'item' NO está en 'lista'
   Ejemplo: assertNotIn("Tostadoras", categorias) ✅

9. assertGreater(A, B)
   → Verifica que A > B (A es mayor que B)
   Ejemplo: assertGreater(producto.stock, 0) ✅
   
10. assertGreaterEqual(A, B)
    → Verifica que A >= B (A es mayor o igual que B)
    Ejemplo: assertGreaterEqual(producto.precio, 0) ✅

11. assertLess(A, B)
    → Verifica que A < B (A es menor que B)
    Ejemplo: assertLess(descuento, 100) ✅
    
12. assertLessEqual(A, B)
    → Verifica que A <= B (A es menor o igual que B)
    Ejemplo: assertLessEqual(cantidad, stock) ✅

13. assertRaises(Excepcion)
    → Verifica que se LANZA una excepción específica
    Se usa con "with":
    with assertRaises(ValueError):
        funcion_que_debe_fallar()
    Ejemplo: Verificar que crear un producto con precio negativo lanza error

14. assertIsInstance(objeto, Clase)
    → Verifica que 'objeto' es una instancia de 'Clase'
    Ejemplo: assertIsInstance(categoria, Categoria) ✅

15. assertContains(response, texto)
    → (Para tests de vistas) Verifica que 'texto' está en la respuesta HTTP
    Ejemplo: assertContains(response, "Bienvenido") ✅

16. assertRedirects(response, url)
    → (Para tests de vistas) Verifica que redirige a 'url'
    Ejemplo: assertRedirects(response, "/login/") ✅

PATRÓN GENERAL:
- assert + [Condición] + (valores a comparar)
- Si la condición es FALSA → Test FALLA ❌
- Si la condición es VERDADERA → Test PASA ✅
"""


