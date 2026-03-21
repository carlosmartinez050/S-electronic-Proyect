from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra')
    
]