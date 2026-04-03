from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shopping_cart.cart import Carrito
from orders.models import Order, OrderItem

# crate your views here.

@login_required
def checkout_view(request):
    carrito = Carrito(request)

    if carrito.esta_vacio():
        return redirect('shop:home')

    # ── GET: mostrar el formulario ──────────────────────────
    if request.method == 'GET':
        context = {
            'carrito_items':   carrito.get_items(),
            'total_articulos': carrito.total_articulos(),
            'subtotal':        carrito.total_precio(),
            'total':           carrito.total_precio() + 20,
            'descuento':       None,
        }
        return render(request, 'checkout/checkout.html', context)

    # ── POST: el usuario presionó "Finalizar Compra" ────────
    if request.method == 'POST':

        # Leemos cada campo del formulario
        # request.POST es un diccionario con todo lo que el usuario escribió
        nombre     = request.POST.get('nombre', '').strip()
        apellido   = request.POST.get('apellido', '').strip()
        direccion  = request.POST.get('direccion', '').strip()

        # ── Validación básica ───────────────────────────────
        # Si algún campo obligatorio está vacío, regresamos al formulario
        # con un mensaje de error
        if not nombre or not apellido or not direccion:
            messages.error(request, 'Por favor completa todos los campos.')

            # Devolvemos el formulario con los datos que ya escribió
            # para que no tenga que repetir todo
            context = {
                'carrito_items':   carrito.get_items(),
                'total_articulos': carrito.total_articulos(),
                'subtotal':        carrito.total_precio(),
                'total':           carrito.total_precio() + 20,
                'descuento':       None,
                # Estos valores prerellenan el formulario
                'form_data': {
                    'nombre':    nombre,
                    'apellido':  apellido,
                    'direccion': direccion,
                }
            }
            return render(request, 'checkout/checkout.html', context)

        # ── Crear la orden en la BD ─────────────────────────
        subtotal    = carrito.total_precio()
        costo_envio = 20
        total       = subtotal + costo_envio

        # 1. Creamos la orden principal
        orden = Order.objects.create(
            usuario   = request.user,
            nombre    = nombre,
            apellido  = apellido,
            direccion = direccion,
            subtotal  = subtotal,
            costo_envio = costo_envio,
            total     = total,
        )

        # 2. Creamos un OrderItem por cada producto del carrito
        for item in carrito.get_items():
            OrderItem.objects.create(
                orden           = orden,
                producto        = item['producto'],
                nombre_producto = item['producto'].nombre,
                precio_unitario = item['producto'].precio,
                cantidad        = item['cantidad'],
                subtotal        = item['subtotal'],
            )
            
        carrito.limpiar()  # Limpiamos el carrito

        messages.success(request, '¡Pedido recibido! Pronto nos comunicaremos contigo.')
        return redirect('shop:home')