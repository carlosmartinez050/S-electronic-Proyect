from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home
    path('', views.vistaPrincipalProductos, name='home'),
    
    # Detalle de producto (usa slug)
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
    
    
    # Categoría (muestra todos los productos de esa categoría)
    path('categoria/<slug:categoria_slug>/', views.categoria_detalle, name='categoria_detalle'),
    
    # Categoría + Marca (filtra por ambos)
    path('categoria/<slug:categoria_slug>/<slug:marca_slug>/', views.categoria_detalle, name='categoria_marca_detalle'),
    
    # Búsqueda de productos
    path('buscar/', views.busqueda_productos, name='busqueda_productos'),
    
    # destacados
    path('destacados/', views.productos_destacados_lista, name='productos_destacados'),
    
    # nuevos
    path('nuevos/', views.productos_nuevos_lista, name='productos_nuevos'),
    
    # marcas
    path('marcas/', views.marcas_lista, name='marcas_lista'),
    
    # marca específica
    path('marcas/<slug:slug>/', views.marca_detalle_lista, name='marca_detalle'),
    
    # ofertas
    path('ofertas/', views.productos_ofertas_lista, name='productos_ofertas'),
]