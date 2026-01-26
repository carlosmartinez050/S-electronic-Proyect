from django.contrib import admin
from .models import Categoria, Marca, Producto, ImagenProducto

# Register your models here.

# ========== INLINE: Imágenes dentro del producto ==========
class ImagenProductoInline(admin.TabularInline):
    """
    Permite agregar/editar imágenes directamente desde el producto
    """
    model = ImagenProducto # Modelo relacionado
    extra = 1  # Muestra 1 formulario vacío extra
    fields = ['imagen', 'orden', 'es_principal', 'alt_text', 'activo'] # Campos a mostrar
    readonly_fields = [] # No hay campos de solo lectura aquí


# ========== ADMIN: CATEGORIA ==========
@admin.register(Categoria) # decorador para registrar el modelo en el admin
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'orden', 'total_productos', 'fecha_creacion'] # Columnas mostradas en la lista
    list_filter = ['activo', 'fecha_creacion'] # Filtros laterales (sidebar)
    search_fields = ['nombre', 'descripcion'] # Barra de búsqueda
    list_editable = ['activo', 'orden']  # Editar directo desde la lista
    prepopulated_fields = {'slug': ('nombre',)}  # Auto-genera slug al escribir nombre
    
    # Organización del formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion') # Campos en esta sección "Información Básica"
        }),
        ('Media', {
            'fields': ('imagen',)   # Campo de imagen
        }),
        ('Configuración', {
            'fields': ('activo', 'orden') # Campos en sección "Configuración"
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)  # Sección colapsable, esta sección estará oculta por defecto, para verla hay que expandirla
        }),
    )
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion'] # Campos de solo lectura 
    
    # Método para mostrar total de productos en la categoría
    def total_productos(self, obj):
        """Muestra cantidad de productos en columna"""
        return obj.total_productos()
    total_productos.short_description = 'Productos Activos'


# ========= ADMIN: MARCA ==========
@admin.register(Marca) # decorador para registrar el modelo Marca en el admin
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'orden', 'total_productos', 'fecha_creacion'] # Columnas mostradas en la lista o tabla
    list_filter = ['activo', 'fecha_creacion']  # Filtros laterales (sidebar)
    search_fields = ['nombre', 'descripcion']   # Barra de búsqueda
    list_editable = ['activo']  # Editar directo desde la lista
    prepopulated_fields = {'slug': ('nombre',)} # Auto-genera slug al escribir nombre

    
    # Organización del formulario de edición
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Configuración', {
            'fields': ('activo', 'orden')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def total_productos(self, obj): # Método para mostrar total de productos en la marca
        """Muestra cantidad de productos en columna"""
        return obj.total_productos()
    total_productos.short_description = 'Productos Activos'
    
    
# ========= ADMIN: PRODUCTO ==========
@admin.register(Producto) # decorador para registrar el modelo Producto en el admin
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'marca', 
        'categoria',
        'precio', 
        'stock', 
        'activo', 
        'destacado',
        'nuevo',
        'disponible_badge'
    ]
    list_filter = ['activo', 'destacado', 'nuevo', 'categoria', 'marca', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'sku'] # Barra de búsqueda, incluye SKU, nombre y descripción
    list_editable = ['precio', 'stock', 'activo', 'destacado', 'nuevo']
    prepopulated_fields = {'slug': ('nombre',)}
    
    # Mostrar imágenes DENTRO del formulario de producto
    inlines = [ImagenProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'marca')
        }),
        ('Inventario', {
            'fields': ('sku', 'precio', 'stock')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('especificaciones',),
            'description': 'Formato JSON: {"RAM": "16GB", "Procesador": "Intel i7"}'
        }),
        ('Estado y Visibilidad', {
            'fields': ('activo', 'destacado', 'nuevo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def disponible_badge(self, obj): # Método para mostrar badge de disponibilidad
        """Muestra badge de disponibilidad con colores"""
        if obj.disponible():
            return '✅ Disponible'
        return '❌ Agotado'
    disponible_badge.short_description = 'Disponibilidad'
    
    # Optimizar consultas (evitar N+1)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('categoria', 'marca')

    