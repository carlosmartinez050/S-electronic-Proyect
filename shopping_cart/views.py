from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from shop.models import Producto
from django.views.decorators.http import require_POST
from decimal import Decimal, ROUND_HALF_UP
@require_POST

    # Create your views here.
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    session_carrito = request.session.get('carrito', {})
    
    # Si viene una cantidad específica en POST (para actualizar)
    if request.method == 'POST' and 'cantidad' in request.POST:
        nueva_cantidad = int(request.POST.get('cantidad', 0))
        
        if nueva_cantidad > 0:
            session_carrito[str(producto_id)] = nueva_cantidad
        else:
            session_carrito.pop(str(producto_id), None)
    else:
        # Comportamiento original (agregar 1)
        if str(producto_id) in session_carrito:
            session_carrito[str(producto_id)] += 1
        else:
            session_carrito[str(producto_id)] = 1
    
    request.session['carrito'] = session_carrito
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        ids_productos = session_carrito.keys()
        productos = Producto.objects.filter(id__in=ids_productos)
        
        total_precio = Decimal("0.00")
        total_articulos = 0
        
        for prod in productos:
            cantidad = session_carrito[str(prod.id)]
            total_precio += prod.precio * cantidad
            total_articulos += cantidad
        
        subtotal_producto = producto.precio * session_carrito.get(str(producto_id), 0)

        # aplicar descuento si corresponde
        descuento_aplicado = request.session.get('descuento_aplicado', False)
        if descuento_aplicado and total_precio >= Decimal("15000"):
            total_precio = total_precio * Decimal("0.9")
            subtotal_producto = subtotal_producto * Decimal("0.9")

        return JsonResponse({
            "success": True,
            "subtotal_producto": float(subtotal_producto),  # convertir a float para JS
            "total_precio": float(total_precio),
            "total_articulos": total_articulos,
        })
    
    print("DEBUG CARRITO:", request.session['carrito'])
    return redirect('vistaPrincipalProductos')


def redondear(valor):
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def ver_carrito(request):
    carrito_session = request.session.get('carrito', {})
    
    ids_productos = carrito_session.keys()
    obtener_productos = Producto.objects.filter(id__in=ids_productos)
    
    lista_carrito = []
    total_precio = Decimal("0.00")   # usar Decimal desde el inicio
    total_articulos = 0
    
    for producto in obtener_productos:
        cantidad = carrito_session[str(producto.id)]
        subtotal = producto.precio * cantidad  # producto.precio ya es Decimal
        
        lista_carrito.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal
        })
        
        total_precio += subtotal
        total_articulos += cantidad
    
    # para el descuento
    descuento_aplicado = request.session.get('descuento_aplicado', False)
    if descuento_aplicado and total_precio >= Decimal("15000"):
       total_precio = total_precio * Decimal("0.9")
       for item in lista_carrito:
           item["subtotal"] = item["subtotal"] * Decimal("0.9")
    print("descuento aplicado:", descuento_aplicado)
    
    total_precio = redondear(total_precio)
    
    context = {
        "lista_carrito": lista_carrito,
        "total_precio": total_precio.quantize(Decimal("0.01")),  # redondear a 2 decimales
        "total_articulos": total_articulos,
        "carrito_vacio": len(lista_carrito) == 0,
        "descuento_aplicado": descuento_aplicado
        
    }
    
    return render(request, 'shopping_cart_Template/contenido_carrito.html', context) 
        
        
def eliminar_producto_del_carrito(request, producto_id):
    session_carrito = request.session.get('carrito', {})
    if str(producto_id) in session_carrito:
        session_carrito.pop(str(producto_id))
    request.session['carrito'] = session_carrito
    # Si es AJAX, devuelve los nuevos totales
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        ids_productos = session_carrito.keys()
        productos = Producto.objects.filter(id__in=ids_productos)
        total_precio = 0
        total_articulos = 0
        for prod in productos:
            cantidad = session_carrito[str(prod.id)]
            total_precio += prod.precio * cantidad
            total_articulos += cantidad
        return JsonResponse({
            'success': True,
            'total_precio': total_precio,
            'total_articulos': total_articulos
        })
    return redirect('vistaPrincipalProductos')
        
        
        
def aplicar_descuento(request):
    request.session['descuento_aplicado'] = True
    return JsonResponse({'success': True})


def finalizar_compra(request):
    # Aquí puedes guardar el pedido en BD si quieres,
    # pero por ahora solo limpiamos el carrito
    request.session['carrito'] = {}
    request.session['descuento_aplicado'] = False
    return JsonResponse({'success': True})
