
# Create your models here.

from django.db import models
from django.conf import settings
from shop.models import Producto
from decimal import Decimal


class Carrito(models.Model):
    """
    Un carrito por usuario autenticado.
    
    Por qué OneToOneField y no ForeignKey:
    Un usuario solo puede tener UN carrito activo a la vez.
    OneToOneField lo garantiza a nivel de base de datos.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,       # Si se borra el usuario, se borra su carrito
        related_name='carrito'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def total_articulos(self):
        """Suma todas las cantidades de los items"""
        return sum(item.cantidad for item in self.items.all())

    def total_precio(self):
        """Suma todos los subtotales con descuentos aplicados"""
        return sum(item.subtotal() for item in self.items.all())

    def esta_vacio(self):
        return not self.items.exists()

    def get_items(self):
        """
        Devuelve los items en el mismo formato que usaba el carrito
        de sesión, para no tener que cambiar los templates.
        """
        return [
            {
                'producto': item.producto,
                'cantidad': item.cantidad,
                'subtotal': item.subtotal(),
            }
            for item in self.items.select_related('producto__marca')
        ]

    def __str__(self):
        return f"Carrito de {self.usuario.get_full_name()}"


class ItemCarrito(models.Model):
    """
    Cada línea dentro de un carrito.
    
    Por qué unique_together:
    Un mismo producto no puede aparecer dos veces en el mismo
    carrito. Si agregas el mismo producto, se incrementa la cantidad.
    Esto lo garantizamos en la base de datos, no solo en el código.
    """
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,       # Si se borra el carrito, se borran sus items
        related_name='items'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='items_carrito'
    )
    
    cantidad = models.PositiveIntegerField(default=1)
    
    # Guardamos el precio al momento de agregar (precio final con descuento incluido)
    # Por qué: si el precio o descuento cambia después, el carrito no debe cambiar.
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    # Guardamos el porcentaje de descuento aplicado (para referencia)
    descuento_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Porcentaje de descuento aplicado al momento de agregar"
    )
    
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        # Garantía a nivel DB: un producto, una vez por carrito
        unique_together = [['carrito', 'producto']]

    def subtotal(self):
        """Calcula el subtotal usando el precio unitario con descuento"""
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"