from django.db import models
from django.utils import timezone
from django.conf import settings       # Para referenciar el usuario
from shop.models import Producto

# Create your models here.

class Order(models.Model):
    """
    Representa una orden de compra completa.
    Se crea cuando el usuario confirma el checkout.
    """

    # ── Estados posibles de una orden ──────────────────────
    # Usamos choices para que solo estos valores sean válidos en BD
    ESTADO_PENDIENTE   = 'pendiente'
    ESTADO_CONFIRMADO  = 'confirmado'
    ESTADO_ENVIADO     = 'enviado'
    ESTADO_ENTREGADO   = 'entregado'
    ESTADO_CANCELADO   = 'cancelado'

    ESTADOS = [
        (ESTADO_PENDIENTE,  'Pendiente'),
        (ESTADO_CONFIRMADO, 'Confirmado'),
        (ESTADO_ENVIADO,    'Enviado'),
        (ESTADO_ENTREGADO,  'Entregado'),
        (ESTADO_CANCELADO,  'Cancelado'),
    ]

    # ── Relación con el usuario ─────────────────────────────
    # on_delete=SET_NULL significa: si el usuario se borra,
    # la orden queda huérfana pero NO se borra. Importante para historial.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes'
    )

    # ── Datos de envío ──────────────────────────────────────
    # Guardamos los datos tal como los escribió el usuario.
    # No hacemos FK a una dirección porque el usuario puede cambiar
    # su dirección después y la orden histórica debe preservar la original.
    nombre    = models.CharField(max_length=100)
    apellido  = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    # ── Totales ─────────────────────────────────────────────
    subtotal     = models.DecimalField(max_digits=10, decimal_places=2)
    costo_envio  = models.DecimalField(max_digits=10, decimal_places=2, default=20)
    total        = models.DecimalField(max_digits=10, decimal_places=2)

    # ── Estado y fechas ─────────────────────────────────────
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE
    )

    fecha_creacion     = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-fecha_creacion']   # Las más recientes primero

    def __str__(self):
        return f'Orden #{self.id} — {self.nombre} {self.apellido}'


class OrderItem(models.Model):
    """
    Cada producto dentro de una orden.
    Es una "foto" del producto al momento de la compra.
    """

    # Si la orden se borra, sus items también se borran
    orden = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # SET_NULL: si el producto se borra del catálogo,
    # el item histórico queda pero con producto=None
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True
    )

    # Guardamos el nombre y precio AL MOMENTO de la compra
    # Así si el producto cambia de precio mañana, la orden no se altera
    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad        = models.PositiveIntegerField()
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Orden'

    def __str__(self):
        return f'{self.cantidad}x {self.nombre_producto}'