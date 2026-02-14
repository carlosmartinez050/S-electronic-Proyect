from django.shortcuts import render, get_object_or_404
from . models import Categoria, Producto, Marca


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
    
    return render(request, 'home/index.html', {
        'productos': productos_recientes,  # ← Mostrar recientes en el cuerpo principal
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
        'productos_recientes': productos_recientes,
        # ← NO pasamos 'marcas' ni 'categoria'
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

def categoria_marca_detalle(request, categoria_slug, marca_slug):
    """
    Filtra productos por categoría Y marca
    URL: /categoria/telefonos/samsung/
    """
    categoria = get_object_or_404(Categoria, slug=categoria_slug, activo=True)
    marca = get_object_or_404(Marca, slug=marca_slug, activo=True)
    
    # Todas las marcas de esta categoría (para la barra azul)
    marcas = Marca.objects.filter(
        productos__categoria=categoria,
        productos__activo=True,
        activo=True
    ).distinct().order_by('orden', 'nombre')
    
    # Productos filtrados por categoría Y marca
    productos = Producto.objects.filter(
        categoria=categoria,
        marca=marca,
        activo=True,
        stock__gt=0
    ).select_related('categoria', 'marca').order_by('-destacado', '-fecha_creacion')
    
    return render(request, 'base.html', {
        'categoria': categoria,
        'marca_seleccionada': marca,  # ← Para resaltar en la barra
        'marcas': marcas,
        'productos': productos,
    })


# def detalle_producto(request, producto_id):
#     detalle_producto = get_object_or_404(Producto, id=producto_id)
#     return render(request, "shop_Template/detalle_producto.html", {
#         'detalle_producto': detalle_producto
#     })
    


















# ---------------------------------------------------------------------------------#

#* INSERCION DE DATOS PARA LOS PRODUCTOS.

# def guardarcategorias(reques):



#     nombres = [
#         "Laptops",
#         "Monitores",
#         "Teclados",
#         "Mouse",
#         "Auriculares",
#         "Tarjetas Gráficas",
#         "Procesadores",
#         "Memorias RAM",
#         "Audífonos",
#         "Case Gamer",
#         "Motherboards",
#         "Fan Cooler",
#         "Almacenamiento"
#     ]


#     categorias = [Categoria(nombre=nombre) for nombre in nombres]   


#     Categoria.objects.bulk_create(categorias)




# def guardarProductos(request):
#         # Obtener todas las categorías existentes en un diccionario por nombre
#     categorias = {cat.nombre: cat for cat in Categoria.objects.all()}

#     productos_data = [
          
#             {
#                 "nombre": "Mouse Razer DeathAdder V2",
#                 "descripcion": "Precisión y velocidad para gamers exigentes.",
#                 "categoria": categorias.get("Mouse"),
#                 "precio": 1800.00,
#                 "imagen": "https://m.media-amazon.com/images/I/41iLtLRTsZL._UF1000,1000_QL80_.jpg",
#             },
#             {
#                 "nombre": "Monitor Samsung Odyssey G5",
#                 "descripcion": "Curvatura envolvente y alta tasa de refresco.",
#                 "categoria": categorias.get("Monitores"),
#                 "precio": 6500.00,
#                 "imagen": "https://sis.omega.com.do/ProductImages/7f94c33b-7b03-4586-b9ff-bff2464706cc.png",
#             },
#             {
#                 "nombre": "Auriculares HyperX Cloud II",
#                 "descripcion": "Sonido envolvente y comodidad para largas sesiones.",
#                 "categoria": categorias.get("Auriculares"),
#                 "precio": 2200.00,
#                 "imagen": "https://m.media-amazon.com/images/I/71ltsViEA8L._UF894,1000_QL80_.jpg",
#             },
#             {
#                 "nombre": "Tarjeta Gráfica NVIDIA RTX 4060",
#                 "descripcion": "Potencia gráfica para gaming y diseño profesional.",
#                 "categoria": categorias.get("Tarjetas Gráficas"),
#                 "precio": 12000.00,
#                 "imagen": "https://m.media-amazon.com/images/I/71N7BLpLAhL._AC_SL1500_.jpg",
#             },
#             {
#                 "nombre": "Procesador Intel Core i7-12700K",
#                 "descripcion": "Rendimiento superior para tareas exigentes.",
#                 "categoria": categorias.get("Procesadores"),
#                 "precio": 9000.00,
#                 "imagen": "https://m.media-amazon.com/images/I/51NlTpm+7KL._UF894,1000_QL80_.jpg",
#             },
#             {
#                 "nombre": "Memoria RAM Corsair Vengeance 16GB",
#                 "descripcion": "Velocidad y estabilidad para tu PC gamer.",
#                 "categoria": categorias.get("Memorias RAM"),
#                 "precio": 1800.00,
#                 "imagen": "https://m.media-amazon.com/images/I/51Y7ugfDRWS.jpg",
#             },
#             {
#                 "nombre": "Audífonos Logitech G733",
#                 "descripcion": "Inalámbricos, ligeros y con iluminación RGB.",
#                 "categoria": categorias.get("Audífonos"),
#                 "precio": 2100.00,
#                 "imagen": "https://oneclickshop.com/wp-content/uploads/2022/07/g733-black-gallery-1.webp",
#             },
#             {
#                 "nombre": "Case Gamer NZXT H510",
#                 "descripcion": "Diseño minimalista y excelente ventilación.",
#                 "categoria": categorias.get("Case Gamer"),
#                 "precio": 2500.00,
#                 "imagen": "https://m.media-amazon.com/images/I/61Ov9C-7wgL.jpg",
#             },
#             {
#                 "nombre": "Motherboard ASUS ROG Strix B550-F",
#                 "descripcion": "Compatibilidad y rendimiento para AMD Ryzen.",
#                 "categoria": categorias.get("Motherboards"),
#                 "precio": 4200.00,
#                 "imagen": "https://dlcdnimgs.asus.com/websites/global/products/uri12btqafuvwte6/img/kv/pd.png",
#             },
#             {
#                 "nombre": "Fan Cooler Cooler Master Hyper 212",
#                 "descripcion": "Refrigeración eficiente para tu procesador.",
#                 "categoria": categorias.get("Fan Cooler"),
#                 "precio": 900.00,
#                 "imagen": "https://a.storyblok.com/f/281110/1500x1500/ebdd2ef6b1/hyper-212-black-01-gallery-05.png/m/960x0/smart",
#             },
#             {
#                 "nombre": "SSD Samsung 970 EVO 1TB",
#                 "descripcion": "Almacenamiento rápido y confiable para tu PC.",
#                 "categoria": categorias.get("Almacenamiento"),
#                 "precio": 3200.00,
#                 "imagen": "https://m.media-amazon.com/images/I/81KciGMdzhL.jpg",
#             },
#             {
#                 "nombre": "Laptop Dell Inspiron 15",
#                 "descripcion": "Portátil confiable para uso diario y oficina.",
#                 "categoria": categorias.get("Laptops"),
#                 "precio": 8500.00,
#                 "imagen": "https://dataimport.com/wp-content/uploads/2024/12/Sin-titulo-2025-01-15T103453.808.png",
#             },
#             # 37 productos adicionales generados automáticamente
#         ]

#         # Generar productos adicionales para completar 50
#     nombres_genericos = [
#         ("Teclado Gamer Redragon K552", "Teclados", "https://cdn.hooli.com.do/wp-content/uploads/2020/02/02202609/front-16.jpg"),
#         ("Mouse Logitech G502 Hero", "Mouse", "https://cdn.hooli.com.do/wp-content/uploads/2020/03/02202319/front-1.jpg"),
#         ("Monitor LG UltraGear 27", "Monitores", "https://www.lg.com/cac/images/monitores/md07570592/gallery/d2.jpg"),
#         ("Auriculares Corsair HS50", "Auriculares", "https://m.media-amazon.com/images/I/61gteQTqlUL._AC_SL1500_.jpg"),
#         ("Tarjeta Gráfica AMD Radeon RX 6600", "Tarjetas Gráficas", "https://m.media-amazon.com/images/I/71Exns6BrvL._AC_SL1500_.jpg"),
#         ("Procesador AMD Ryzen 5 5600X", "Procesadores", "https://www.invidcomputers.com/images/000000000041306882104413068.png"),
#         ("Memoria RAM Kingston Fury 16GB", "Memorias RAM", "https://m.media-amazon.com/images/I/61MYgWr+xWL._UF894,1000_QL80_.jpg"),
#         ("Audífonos Razer Kraken X", "Audífonos", "https://m.media-amazon.com/images/I/61Id4s0lMnL._UF894,1000_QL80_.jpg"),
#         ("Case Gamer Thermaltake V200", "Case Gamer", "https://www.avantechsystem.com/wp-content/uploads/2023/05/v200-5.webp"),
#         ("Motherboard MSI B450 Tomahawk", "Motherboards", "https://m.media-amazon.com/images/I/61dC+ExLsvL.jpg"),
#         ("Fan Cooler Noctua NH-D15", "Fan Cooler", "https://m.media-amazon.com/images/I/81i9YOlnPEL.jpg"),
#         ("SSD Kingston A2000 500GB", "Almacenamiento", "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiZU12EgZakKHlpITy31Hu6wB99mJSGLIMiNy3BGIO9BQS_7Rd5wt4auyutj87FmctzOeJSC02rQX_vCwdqQgGVFSj0SIhI1MrHRfWvUPCUb-KShJrJKx1WUe_x3QjUd7C2BK-yPiDj0pYF/s1600/hexmojo-kingston-a2000-review-1.jpg"),
#         ("Laptop HP Pavilion Gaming", "Laptops", "https://casacuesta.com/media/catalog/product/cache/fde49a4ea9a339628caa0bc56aea00ff/3/3/3340418-2__1700678743.jpg"),
#     ]
#     # Repetir y variar para llegar a 50 productos
#     for i in range(36):
#         nombre, categoria_nombre, imagen = nombres_genericos[i % len(nombres_genericos)]
#         productos_data.append({
#             "nombre": f"{nombre} #{i+2}",
#             "descripcion": f"Producto de alta calidad para PC gamer y convencional, modelo {i+2}.",
#             "categoria": categorias.get(categoria_nombre),
#             "precio": 2000.00 + (i * 100),
#             "imagen": imagen,
#         })
#     productos = [
#         Producto(
#             nombre=prod["nombre"],
#             descripcion=prod["descripcion"],
#             categoria=prod["categoria"],
#             precio=prod["precio"],
#             stock=50,
#             imagen=prod["imagen"]
#         )
#         for prod in productos_data
#     ]
#     Producto.objects.bulk_create(productos)
   
