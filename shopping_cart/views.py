from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from shop.models import Producto
from shopping_cart.cart import Carrito
from django.views.decorators.http import require_POST


# Create your views here.
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)

    if 'cantidad' in request.POST:
        cantidad = int(request.POST.get('cantidad'))
        carrito.agregar(producto, cantidad=cantidad, actualizar=True)
    else:
        carrito.agregar(producto)

    items = carrito.get_items()
    item_actualizado = next(
        (i for i in items if i['producto'].id == producto_id),
        None
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_articulos': carrito.total_articulos(),
            'total_precio': float(carrito.total_precio()),
            'subtotal_producto': float(item_actualizado['subtotal']) if item_actualizado else 0,
        })

    return redirect('shop:home')


def ver_carrito(request):
    carrito = Carrito(request)

    context = {
        'lista_carrito': carrito.get_items(),     
        'total_precio': carrito.total_precio(),       
        'total_articulos': carrito.total_articulos(),    
        'carrito_vacio': carrito.esta_vacio(),     
    }

    return render(request, 'shopping_cart_Template/contenido_carrito.html', context)
            
        
@require_POST
def eliminar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.eliminar(producto)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_articulos': carrito.total_articulos(),
            'total_precio': float(carrito.total_precio()),
        })

    return redirect('shop:home')

@require_POST
def finalizar_compra(request):
    # Aquí puedes guardar el pedido en BD si quieres,
    # pero por ahora solo limpiamos el carrito
    carrito = Carrito(request)
    carrito.limpiar()

    return JsonResponse({'success': True})
