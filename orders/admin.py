
# Register your models here.
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Muestra los productos dentro de cada orden"""
    model = OrderItem
    extra = 0                          # Sin filas vacías extra
    readonly_fields = ['nombre_producto', 'precio_unitario', 'cantidad', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'apellido', 'total', 'estado', 'fecha_creacion']
    list_filter   = ['estado', 'fecha_creacion']
    search_fields = ['nombre', 'apellido']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines       = [OrderItemInline]