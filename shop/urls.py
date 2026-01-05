from django.urls import path
from . import views

urlpatterns = [
   path('', views.vistaPrincipalProductos, name='vistaPrincipalProductos'),
   path('productos/<int:categoria_id>/', views.consultaProductoCategoria, name='consultaProductoCategoria' ) ,
   path('detalle_producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto')
]
