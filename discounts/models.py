from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Categoria, Marca, Producto


class DescuentoCategoria(models.Model):
    """
    Descuento aplicable a una categoría completa
    """
    categoria = models.OneToOneField(
        Categoria,
        on_delete=models.CASCADE,
        related_name='descuento',
        help_text="Categoría a la que aplica el descuento"
    )
    
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0-100)"
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de inicio del descuento"
    )
    
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de fin del descuento (vacío = sin límite)"
    )
    
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Activar o desactivar descuento"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del descuento"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Descuento por Categoría"
        verbose_name_plural = "Descuentos por Categoría"
        ordering = ['-fecha_creacion']
    
    def es_valido(self):
        """Verifica si el descuento está activo y dentro del período válido"""
        if not self.activo:
            return False
        ahora = timezone.now()
        if self.fecha_inicio > ahora:
            return False
        if self.fecha_fin and self.fecha_fin < ahora:
            return False
        return True
    
    def clean(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def __str__(self):
        return f"Descuento {self.porcentaje}% - {self.categoria.nombre}"


class DescuentoMarca(models.Model):
    """
    Descuento aplicable a una marca completa
    """
    marca = models.OneToOneField(
        Marca,
        on_delete=models.CASCADE,
        related_name='descuento',
        help_text="Marca a la que aplica el descuento"
    )
    
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0-100)"
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de inicio del descuento"
    )
    
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de fin del descuento (vacío = sin límite)"
    )
    
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Activar o desactivar descuento"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del descuento"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Descuento por Marca"
        verbose_name_plural = "Descuentos por Marca"
        ordering = ['-fecha_creacion']
    
    def es_valido(self):
        """Verifica si el descuento está activo y dentro del período válido"""
        if not self.activo:
            return False
        ahora = timezone.now()
        if self.fecha_inicio > ahora:
            return False
        if self.fecha_fin and self.fecha_fin < ahora:
            return False
        return True
    
    def clean(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def __str__(self):
        return f"Descuento {self.porcentaje}% - {self.marca.nombre}"


class DescuentoProducto(models.Model):
    """
    Descuento aplicable a un producto individual
    Tiene mayor prioridad que los descuentos de categoría y marca
    """
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name='descuento',
        help_text="Producto al que aplica el descuento"
    )
    
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0-100)"
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de inicio del descuento"
    )
    
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de fin del descuento (vacío = sin límite)"
    )
    
    activo = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Activar o desactivar descuento"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción del descuento"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Descuento por Producto"
        verbose_name_plural = "Descuentos por Producto"
        ordering = ['-fecha_creacion']
    
    def es_valido(self):
        """Verifica si el descuento está activo y dentro del período válido"""
        if not self.activo:
            return False
        ahora = timezone.now()
        if self.fecha_inicio > ahora:
            return False
        if self.fecha_fin and self.fecha_fin < ahora:
            return False
        return True
    
    def clean(self):
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def __str__(self):
        return f"Descuento {self.porcentaje}% - {self.producto.nombre}"
