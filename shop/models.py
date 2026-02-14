import time
from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError


# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        db_index=True
    )
    
    descripcion = models.TextField(blank=True)
    
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        help_text="Imagen representativa de la categoría"
    )
    
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    
    fecha_creacion = models.DateTimeField(default=timezone.now, editable=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['activo', 'orden']),
            models.Index(fields=['slug', 'activo']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
            original_slug = self.slug
            counter = 1
            while Categoria.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.nombre:
            self.nombre = ' '.join(self.nombre.split()).strip()
        if not self.nombre:
            raise ValidationError({'nombre': 'El nombre no puede estar vacío'})
    
    def productos_activos(self):
        return self.productos.filter(activo=True, stock__gt=0)
    
    def total_productos(self):
        return self.productos_activos().count()
    
    def get_absolute_url(self):
        return reverse('shop:categoria_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.nombre


# --------------------------------------------------------------------------------- #

class Marca(models.Model):
    """
    Marcas de productos (Dell, HP, Samsung, LG, etc.)
    Permite filtrar productos por fabricante
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Nombre de la marca (ej: Dell, Samsung, Logitech)"
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        db_index=True
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción de la marca"
    )
    
    logo = models.ImageField(
        upload_to='marcas/',
        blank=True,
        null=True,
        help_text="URL del logo de la marca"
    )
    
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Marca visible en filtros"
    )
    
    # Ordenamiento manual (ej: marcas populares primero)
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden en filtros (menor = primero)"
    )
    
    fecha_creacion = models.DateTimeField(default=timezone.now, editable=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['activo', 'orden']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)    #  slugify() convierte el slug a miniusculas automaticamente
            original_slug = self.slug
            counter = 1
            while Marca.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.nombre:
            self.nombre = ' '.join(self.nombre.split()).strip()
        if not self.nombre:
            raise ValidationError({'nombre': 'El nombre no puede estar vacío'})
    
    def productos_activos(self):
        """Productos activos de esta marca"""
        return self.productos.filter(activo=True, stock__gt=0)
    
    def total_productos(self):
        """Cuenta productos activos"""
        return self.productos_activos().count()
    
    def get_absolute_url(self):
        return reverse('shop:marca_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.nombre


# --------------------------------------------------------------------------------- #

class Producto(models.Model):
    """
    Producto de e-commerce de electrónicos
    """
    # ========== INFORMACIÓN BÁSICA ==========
    nombre = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Nombre completo del producto"
    )
    
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        db_index=True
    )
    
    descripcion = models.TextField(
        help_text="Descripción detallada con características técnicas",
        blank=True,
        default=''
    )
    
    # ========== RELACIONES ==========
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        help_text="Categoría del producto",
        null=True,
        blank=True
    )
    
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,  # ← No puedes borrar marca con productos
        related_name='productos',
        help_text="Fabricante del producto",
        null=True,
        blank=True
    )
    
    # ========== IDENTIFICACIÓN ==========
    sku = models.CharField(
        "SKU",
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Código único de inventario"
    )
    
    # ========== PRECIO Y STOCK ==========
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de venta"
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad disponible"
    )
    
    # ========== CARACTERÍSTICAS TÉCNICAS ==========
    especificaciones = models.JSONField(
        default=dict,
        blank=True,
        help_text="Especificaciones técnicas en formato JSON"
    )
    # Ejemplo laptop: {"RAM": "16GB", "Procesador": "Intel i7", "Pantalla": "15.6"}
    # Ejemplo mouse: {"DPI": "16000", "Conectividad": "Bluetooth", "Botones": "8"}
    
    # ========== ESTADO Y VISIBILIDAD ==========
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Producto visible en tienda"
    )
    
    destacado = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Mostrar en página principal"
    )
    
    nuevo = models.BooleanField(
        default=False,
        help_text="Etiquetar como 'Nuevo'"
    )
    
    # ========== METADATA ==========
    fecha_creacion = models.DateTimeField(default=timezone.now, editable=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
        indexes = [ # Índices para búsquedas comunes
            models.Index(fields=['slug', 'activo']),
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['marca', 'activo']),
            models.Index(fields=['activo', 'destacado']),
        ]
        constraints = [ # Restricción para precio no negativo
            models.CheckConstraint(
                check=models.Q(precio__gte=0),
                name='precio_no_negativo'
            ),
        ]
    
    def save(self, *args, **kwargs):
        
        if not self.marca_id:
            raise ValidationError('El producto debe tener una marca asignada')
        
        # Auto-generar slug
        if not self.slug:
            base_slug = slugify(self.nombre)
            self.slug = base_slug
            counter = 1
            while Producto.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Auto-generar SKU
        if not self.sku: # el SKU se genera si no existe
            marca_code = self.marca.nombre[:4].upper() if self.marca else "PROD"
            timestamp = int(time.time() * 1000)  # milisegundos
            self.sku = f"{marca_code}-{timestamp}"
        
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.precio and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo'})
    
    # ========== MÉTODOS ÚTILES ==========
    
    def disponible(self):
        """¿Disponible para compra?"""
        return self.activo and self.stock > 0
    
    def get_imagen_principal(self):
        """Retorna la imagen principal o None"""
        return self.imagenes.filter(es_principal=True, activo=True).first()
    
    def get_imagenes_secundarias(self):
        """Retorna imágenes adicionales (no principal)"""
        return self.imagenes.filter(es_principal=False, activo=True).order_by('orden')
    
    def get_todas_imagenes(self):
        """Retorna todas las imágenes ordenadas"""
        return self.imagenes.filter(activo=True).order_by('orden')
    
    def tiene_imagenes(self):
        """¿Tiene al menos una imagen?"""
        return self.imagenes.filter(activo=True).exists()
    
    def get_absolute_url(self):
        return reverse('shop:producto_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"
    
# --------------------------------------------------------------------------------- #


class ImagenProducto(models.Model):
    """
    Galería de imágenes de productos
    Relación 1 Producto → N Imágenes
    """
    producto = models.ForeignKey(
        'Producto',  # ← Usamos string porque Producto se define después
        on_delete=models.CASCADE,  # ← Si borras producto, se borran sus imágenes
        related_name='imagenes', # related_name se usa para acceder a las imágenes desde el producto
        help_text="Producto al que pertenece esta imagen"
    )
    
    imagen = models.ImageField(
        upload_to='productos/',
        help_text="URL de la imagen del producto"
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización (0 = imagen principal)"
    )
    
    es_principal = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Imagen que se muestra en listados"
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Texto alternativo para SEO y accesibilidad"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Imagen visible en galería"
    )
    
    fecha_creacion = models.DateTimeField(default=timezone.now, editable=False)
    
    # ========= METADATA ========== "clase que define metadatos del modelo, como el nombre legible, el ordenamiento predeterminado y los índices de la base de datos."
    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Producto"
        ordering = ['orden', 'id']
        indexes = [
            models.Index(fields=['producto', 'orden']),
            models.Index(fields=['producto', 'es_principal']),
        ]
    
    # ========= MÉTODOS ========== "métodos personalizados para el modelo, como la lógica de guardado y la representación en cadena."
    def save(self, *args, **kwargs):
        # Si es principal, quitar flag de otras imágenes del mismo producto
        if self.es_principal:
            ImagenProducto.objects.filter(
                producto=self.producto,             # el metodo save() asegura que solo una imagen por producto sea la principal
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        
        # Auto-generar alt_text si no existe
        if not self.alt_text and self.producto:
            self.alt_text = f"{self.producto.nombre} - Imagen {self.orden + 1}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        principal = " (Principal)" if self.es_principal else ""
        return f"{self.producto.nombre} - Imagen {self.orden}{principal}"
    
 