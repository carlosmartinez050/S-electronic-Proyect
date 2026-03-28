from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home
    path('', views.vistaPrincipalProductos, name='home'),
    
    # Detalle de producto (usa slug)
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
    
    # Productos destacados
    # path('productos-destacados/', views.productos_destacados_lista, name='productos_destacados'),
    
    # Categoría (muestra todos los productos de esa categoría)
    path('categoria/<slug:slug>/', views.categoria_detalle, name='categoria_detalle'),
    
    # Categoría + Marca (filtra por ambos)
    path('categoria/<slug:categoria_slug>/<slug:marca_slug>/',views.categoria_detalle, name='categoria_detalle'),
    
    # Búsqueda de productos
    path('buscar/', views.busqueda_productos, name='busqueda_productos'),
]