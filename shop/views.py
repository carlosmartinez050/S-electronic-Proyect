from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from . models import Categoria, Producto, Marca
from django.shortcuts import redirect

# Create your views here.
def vistaPrincipalProductos(request):
    """
    Home - Muestra productos de TODAS las categorías
    Barra azul: VACÍA
    """
    # Productos destacados (de todas las categorías)
    productos_destacados = Producto.objects.filter(
        activo=True,
        destacado=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]
        
    # Productos nuevos (de todas las categorías)
    productos_nuevos = Producto.objects.filter(
        activo=True,
        nuevo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]
    
    # Productos recientes (de todas las categorías)
    productos_recientes = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:20]
    
    # productos_ofertas = Producto.objects.filter(          #* FUTURA SECCIÓN DE OFERTAS *) ESPERA A SER IMPLEMENTADA EN EL FUTURO, CON LA APP "DESCUENTOS".
    #     oferta=True,
    #     stock__gt=0
    # ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]
    
    marcas = Marca.objects.filter(
        activo=True
    ).order_by('orden', 'nombre')
    
    return render(request, 'home/index.html', {
        'productos': productos_recientes,  # ← Mostrar recientes en el cuerpo principal
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
        'marcas': marcas,  
        # 'productos_ofertas': productos_ofertas,  
    })
    
    
def categoria_detalle(request, slug):
    """
    Muestra productos de una categoría específica
    URL: /categoria/telefonos/
    """
    categoria = get_object_or_404(Categoria, slug=slug, activo=True)
    
    # Marcas que tienen productos en esta categoría
    marcas = Marca.objects.filter(
        productos__categoria=categoria,
        productos__activo=True,
        activo=True
    ).distinct().order_by('orden', 'nombre')
    
    # Productos de esta categoría
    productos = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-destacado', '-fecha_creacion')
    
    return render(request, 'base.html', {
        'categoria': categoria,
        'marcas': marcas,  # ← Para la barra azul
        'productos': productos,
    })

def categoria_detalle(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug, activo=True)

    # 🟣 POPULARES (puedes cambiar la lógica luego)
    productos_populares = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0,
        destacado=True   # usamos destacado como "popular"
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]

    # 🔵 RECOMENDADOS (por ahora: recientes)
    productos_recomendados = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]

    # 🟡 OFERTAS (cuando implementes descuentos)
    productos_ofertas = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0,
        # oferta=True  ← cuando lo tengas
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]

    return render(request, 'shop_Template/categoria_detalle.html', {
        'categoria': categoria,
        'productos_populares': productos_populares,
        'productos_recomendados': productos_recomendados,
        'productos_ofertas': productos_ofertas,
    })


def detalle_producto(request, slug):
    """
    Muestra el detalle de un producto específico
    URL: /producto/razer-deathadder-v2/
    """
    # Obtener el producto por slug, asegurándose de que esté activo
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    
    # buscar productos relacionados o similares.
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True,
        stock__gt=0
    ).exclude(
        id=producto.id
    ).select_related(
        'categoria', 'marca'
    ).order_by('-destacado', '-fecha_creacion')[:8]
    
    return render(request, 'shop_Template/detalle_producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'detalle_producto': producto,
    })
    

def productos_destacados_lista(request):
    productos = Producto.objects.filter(activo=True, destacado=True, stock__gt=0)
    return render(request, 'shop_Template/productos_lista.html', {
        'productos': productos
    })

 

# VISTA PARA LA BUSQUEDA DE PRODUCTOS (INPUT DE BUSQUEDA EN EL HEADER)
def busqueda_productos(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        # Si no hay consulta, redirigir a la página principal o mostrar un mensaje
        return redirect('shop:home')  
    
    productos = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(categoria__nombre__icontains=query) |
        Q(marca__nombre__icontains=query)
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')
    
    return render(request, 'shop_Template/productos_lista.html', {
        'productos': productos,
        'query': query,
    })
    











