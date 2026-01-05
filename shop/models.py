from django.db import models

# Create your models here.

 
#* CLASSE MODELO CATEGORIA.
class Categoria(models.Model):
    nombre = models.CharField()
    
    
    
#* CLASSE MODELO PRODUCTOS.
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen = models.URLField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)