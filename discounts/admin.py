from django.contrib import admin
from django.utils import timezone
from .models import DescuentoCategoria, DescuentoMarca, DescuentoProducto


class BaseDescuentoAdmin(admin.ModelAdmin):
    """Base para los admins de descuentos"""
    list_display = ['get_nombre', 'porcentaje', 'activo', 'fecha_inicio', 'fecha_fin', 'es_valido_display']
    list_filter = ['activo', 'fecha_inicio', 'fecha_fin']
    search_fields = ['descripcion']
    fieldsets = (
        ('Información Básica', {
            'fields': ['porcentaje', 'activo', 'descripcion']
        }),
        ('Período de Validez', {
            'fields': ['fecha_inicio', 'fecha_fin'],
            'description': 'Define el período en el que el descuento es válido'
        }),
    )
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def es_valido_display(self, obj):
        """Muestra si el descuento está actualmente válido"""
        if obj.es_valido():
            return '✅ Válido'
        return '❌ Inválido'
    es_valido_display.short_description = 'Estado Actual'


@admin.register(DescuentoCategoria)
class DescuentoCategoriaAdmin(BaseDescuentoAdmin):
    fieldsets = (
        ('Categoría', {
            'fields': ['categoria']
        }),
        ('Información Básica', {
            'fields': ['porcentaje', 'activo', 'descripcion']
        }),
        ('Período de Validez', {
            'fields': ['fecha_inicio', 'fecha_fin'],
            'description': 'Define el período en el que el descuento es válido'
        }),
        ('Metadata', {
            'fields': ['fecha_creacion', 'fecha_actualizacion'],
            'classes': ['collapse']
        }),
    )
    
    def get_nombre(self, obj):
        return f"{obj.categoria.nombre}"
    get_nombre.short_description = "Categoría"


@admin.register(DescuentoMarca)
class DescuentoMarcaAdmin(BaseDescuentoAdmin):
    fieldsets = (
        ('Marca', {
            'fields': ['marca']
        }),
        ('Información Básica', {
            'fields': ['porcentaje', 'activo', 'descripcion']
        }),
        ('Período de Validez', {
            'fields': ['fecha_inicio', 'fecha_fin'],
            'description': 'Define el período en el que el descuento es válido'
        }),
        ('Metadata', {
            'fields': ['fecha_creacion', 'fecha_actualizacion'],
            'classes': ['collapse']
        }),
    )
    
    def get_nombre(self, obj):
        return f"{obj.marca.nombre}"
    get_nombre.short_description = "Marca"


@admin.register(DescuentoProducto)
class DescuentoProductoAdmin(BaseDescuentoAdmin):
    fieldsets = (
        ('Producto', {
            'fields': ['producto']
        }),
        ('Información Básica', {
            'fields': ['porcentaje', 'activo', 'descripcion']
        }),
        ('Período de Validez', {
            'fields': ['fecha_inicio', 'fecha_fin'],
            'description': 'Define el período en el que el descuento es válido'
        }),
        ('Metadata', {
            'fields': ['fecha_creacion', 'fecha_actualizacion'],
            'classes': ['collapse']
        }),
    )
    
    def get_nombre(self, obj):
        return f"{obj.producto.nombre}"
    get_nombre.short_description = "Producto"
