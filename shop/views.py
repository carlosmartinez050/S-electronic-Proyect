from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from . models import Categoria, Producto, Marca
from django.shortcuts import redirect
from discounts.models import DescuentoProducto, DescuentoCategoria, DescuentoMarca

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
    
    # Productos con ofertas (descuentos activos) - CON MANEJO DE ERRORES
    productos_ofertas = []
    try:
        # Obtener IDs de productos con descuentos válidos
        productos_con_descuento_ids = set()
        
        # 1. Productos con descuento individual
        descuentos_producto = DescuentoProducto.objects.filter(
            activo=True
        ).select_related('producto')
        for desc in descuentos_producto:
            try:
                if desc.es_valido():
                    productos_con_descuento_ids.add(desc.producto.id)
            except Exception:
                continue
        
        # 2. Productos de categorías con descuento
        descuentos_categoria = DescuentoCategoria.objects.filter(
            activo=True
        ).select_related('categoria')
        for desc in descuentos_categoria:
            try:
                if desc.es_valido():
                    productos = Producto.objects.filter(
                        categoria=desc.categoria,
                        activo=True,
                        stock__gt=0
                    )
                    for prod in productos:
                        productos_con_descuento_ids.add(prod.id)
            except Exception:
                continue
        
        # 3. Productos de marcas con descuento
        descuentos_marca = DescuentoMarca.objects.filter(
            activo=True
        ).select_related('marca')
        for desc in descuentos_marca:
            try:
                if desc.es_valido():
                    productos = Producto.objects.filter(
                        marca=desc.marca,
                        activo=True,
                        stock__gt=0
                    )
                    for prod in productos:
                        productos_con_descuento_ids.add(prod.id)
            except Exception:
                continue
        
        # Obtener los productos con descuentos
        if productos_con_descuento_ids:
            productos_ofertas = Producto.objects.filter(
                id__in=productos_con_descuento_ids
            ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]
    except Exception:
        # Si hay cualquier error en lógica de descuentos, simplemente ignorar
        productos_ofertas = []
    
    marcas = Marca.objects.filter(
        activo=True
    ).order_by('orden', 'nombre')
    
    return render(request, 'home/index.html', {
        'productos': productos_recientes,  # ← Mostrar recientes en el cuerpo principal
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
        'productos_ofertas': productos_ofertas,
        'marcas': marcas,  
    })
    

    
def categoria_detalle(request, categoria_slug, marca_slug=None):
    """
    Muestra productos de una categoría específica, y opcionalmente filtra por marca
    URL: /categoria/telefonos/ o /categoria/telefonos/apple/
    """
    categoria = get_object_or_404(Categoria, slug=categoria_slug, activo=True)
    ahora = timezone.now()

    # Marcas que tienen productos en esta categoría
    marcas = Marca.objects.filter(
        productos__categoria=categoria,
        productos__activo=True,
        activo=True
    ).distinct().order_by('orden', 'nombre')
    
    # Si se especifica una marca, validar que exista y pertenezca a la categoría
    marca_seleccionada = None
    if marca_slug:
        marca_seleccionada = get_object_or_404(Marca, slug=marca_slug, activo=True)
        # Verificar que la marca tenga productos en esta categoría
        if not Producto.objects.filter(categoria=categoria, marca=marca_seleccionada, activo=True).exists():
            marca_seleccionada = None

    # POPULARES
    query_populares = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0,
        destacado=True
    ).select_related('categoria', 'marca')
    
    if marca_seleccionada:
        query_populares = query_populares.filter(marca=marca_seleccionada)
    
    productos_populares = query_populares.order_by('-fecha_creacion')[:8]

    # RECOMENDADOS
    query_recomendados = Producto.objects.filter(
        categoria=categoria,
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca')
    
    if marca_seleccionada:
        query_recomendados = query_recomendados.filter(marca=marca_seleccionada)
    
    productos_recomendados = query_recomendados.order_by('-fecha_creacion')[:8]

    #  OFERTAS (productos con descuentos válidos de esta categoría) - CON MANEJO DE ERRORES
    productos_ofertas = []
    try:
        productos_con_descuento_ids = set()
        
        # Productos individuales con descuento
        descuentos_producto = DescuentoProducto.objects.filter(
            activo=True,
            producto__categoria=categoria,
            producto__activo=True,
            producto__stock__gt=0
        ).select_related('producto')
        
        if marca_seleccionada:
            descuentos_producto = descuentos_producto.filter(producto__marca=marca_seleccionada)
        
        for desc in descuentos_producto:
            try:
                if desc.es_valido():
                    productos_con_descuento_ids.add(desc.producto.id)
            except Exception:
                continue
        
        # Descuento de la categoría
        try:
            descuento_cat = DescuentoCategoria.objects.get(categoria=categoria, activo=True)
            if descuento_cat.es_valido():
                productos = Producto.objects.filter(
                    categoria=categoria,
                    activo=True,
                    stock__gt=0
                )
                for prod in productos:
                    productos_con_descuento_ids.add(prod.id)
        except DescuentoCategoria.DoesNotExist:
            pass
        except Exception:
            pass
        
        # Descuentos por marca (para productos de esta categoría)
        descuentos_marca = DescuentoMarca.objects.filter(
            activo=True
        ).select_related('marca')
        for desc in descuentos_marca:
            try:
                if desc.es_valido():
                    productos = Producto.objects.filter(
                        marca=desc.marca,
                        categoria=categoria,
                        activo=True,
                        stock__gt=0
                    )
                    if marca_seleccionada:
                        productos = productos.filter(marca=marca_seleccionada)
                    for prod in productos:
                        productos_con_descuento_ids.add(prod.id)
            except Exception:
                continue
        
        if productos_con_descuento_ids:
            productos_ofertas = Producto.objects.filter(
                id__in=productos_con_descuento_ids
            ).select_related('categoria', 'marca').order_by('-fecha_creacion')[:8]
    except Exception:
        # Si hay cualquier error, simplemente ignorar ofertas
        productos_ofertas = []

    return render(request, 'shop_Template/categoria_detalle.html', {
        'categoria': categoria,
        'marcas': marcas,
        'marca_seleccionada': marca_seleccionada,
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
    productos = Producto.objects.filter(
        activo=True,
        destacado=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')

    return render(request, 'shop_Template/productos_lista.html', {
        'productos':      productos,
        'titulo_pagina':  'Productos Destacados',
        'subtitulo':      f'{productos.count()} productos encontrados',
    })


def productos_nuevos_lista(request):
    productos = Producto.objects.filter(
        activo=True,
        nuevo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')

    return render(request, 'shop_Template/productos_lista.html', {
        'productos':      productos,
        'titulo_pagina':  'Productos Nuevos',
        'subtitulo':      f'{productos.count()} productos encontrados',
    })
    

def marcas_lista(request):
    """Todos los productos de todas las marcas"""
    productos = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('marca__nombre', '-fecha_creacion')

    return render(request, 'shop_Template/productos_lista.html', {
        'productos':      productos,
        'titulo_pagina':  'Todas las Marcas',
        'subtitulo':      f'{productos.count()} productos encontrados',
    })
    
    
def marca_detalle_lista(request, slug):
    """Productos de una marca específica"""
    marca = get_object_or_404(Marca, slug=slug, activo=True)

    productos = Producto.objects.filter(
        marca=marca,
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-fecha_creacion')

    return render(request, 'shop_Template/productos_lista.html', {
        'productos':      productos,
        'titulo_pagina':  f'Productos {marca.nombre}',
        'subtitulo':      f'{productos.count()} productos encontrados',
    })
 
 
def productos_ofertas_lista(request):
    """Lista de productos con ofertas válidas"""
    productos_ofertas = []
    
    try:
        productos_con_descuento_ids = set()
        
        # 1. Productos con descuento individual
        descuentos_producto = DescuentoProducto.objects.filter(
            activo=True
        ).select_related('producto')
        for desc in descuentos_producto:
            try:
                if desc.es_valido():
                    productos_con_descuento_ids.add(desc.producto.id)
            except Exception:
                continue
        
        # 2. Productos de categorías con descuento
        descuentos_categoria = DescuentoCategoria.objects.filter(
            activo=True
        ).select_related('categoria')
        for desc in descuentos_categoria:
            try:
                if desc.es_valido():
                    productos = Producto.objects.filter(
                        categoria=desc.categoria,
                        activo=True,
                        stock__gt=0
                    )
                    for prod in productos:
                        productos_con_descuento_ids.add(prod.id)
            except Exception:
                continue
        
        # 3. Productos de marcas con descuento
        descuentos_marca = DescuentoMarca.objects.filter(
            activo=True
        ).select_related('marca')
        for desc in descuentos_marca:
            try:
                if desc.es_valido():
                    productos = Producto.objects.filter(
                        marca=desc.marca,
                        activo=True,
                        stock__gt=0
                    )
                    for prod in productos:
                        productos_con_descuento_ids.add(prod.id)
            except Exception:
                continue
        
        if productos_con_descuento_ids:
            productos_ofertas = Producto.objects.filter(
                id__in=productos_con_descuento_ids
            ).select_related('categoria', 'marca').order_by('-fecha_creacion')
    except Exception:
        productos_ofertas = []

    return render(request, 'shop_Template/productos_lista.html', {
        'productos':      productos_ofertas,
        'titulo_pagina':  'Ofertas Especiales',
        'subtitulo':      f'{productos_ofertas.count()} productos encontrados',
    })


# VISTA PARA LA BUSQUEDA DE PRODUCTOS (INPUT DE BUSQUEDA EN EL HEADER)
def busqueda_productos(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        # Si no hay consulta, redirigir a la página principal
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
        'titulo_pagina': f'Resultados de búsqueda: "{query}"',
        'subtitulo': f'{productos.count()} productos encontrados',
    })
    











