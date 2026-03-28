# shopping_cart/cart.py

from decimal import Decimal
from shop.models import Producto
from .models import Carrito as CarritoDB, ItemCarrito


class Carrito:
    def __init__(self, request):
        self.request = request
        self.usuario = request.user

        if self.usuario.is_authenticated:
            self._modo = 'db'
            # get_or_create: si no tiene carrito, lo crea automáticamente
            self._carrito_db, _ = CarritoDB.objects.get_or_create(
                usuario=self.usuario
            )
        else:
            self._modo = 'sesion'
            sesion = request.session
            if 'carrito' not in sesion:
                sesion['carrito'] = {}
            self._sesion_data = sesion['carrito']
            self._sesion = sesion

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PÚBLICOS — misma interfaz para DB y sesión
    # ─────────────────────────────────────────────────────────────

    def agregar(self, producto, cantidad=1, actualizar=False):
        """
        Agrega un producto o actualiza su cantidad.
        
        actualizar=False → suma la cantidad al total existente
        actualizar=True  → reemplaza la cantidad (usado en el input de cantidad)
        """
        if producto.stock <= 0:
            return

        if self._modo == 'db':
            self._agregar_db(producto, cantidad, actualizar)
        else:
            self._agregar_sesion(producto, cantidad, actualizar)

    def eliminar(self, producto):
        if self._modo == 'db':
            self._carrito_db.items.filter(producto=producto).delete()
        else:
            producto_id = str(producto.id)
            if producto_id in self._sesion_data:
                del self._sesion_data[producto_id]
                self._guardar_sesion()

    def limpiar(self):
        if self._modo == 'db':
            self._carrito_db.items.all().delete()
        else:
            self._sesion['carrito'] = {}
            self._sesion_data = {}
            self._guardar_sesion()

    def get_items(self):
        """
        Devuelve lista de dicts con producto, cantidad y subtotal.
        Formato idéntico en ambos modos para que los templates funcionen igual.
        """
        if self._modo == 'db':
            return self._carrito_db.get_items()
        else:
            return self._get_items_sesion()

    def total_articulos(self):
        if self._modo == 'db':
            return self._carrito_db.total_articulos()
        else:
            return sum(self._sesion_data.values())

    def total_precio(self):
        return sum(item['subtotal'] for item in self.get_items())

    def esta_vacio(self):
        if self._modo == 'db':
            return self._carrito_db.esta_vacio()
        else:
            return len(self._sesion_data) == 0

    # ─────────────────────────────────────────────────────────────
    # FUSIÓN: sesión → DB al hacer login
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def fusionar_sesion_a_db(request):
        """
        Llama esto justo después del login.
        Mueve los productos del carrito de sesión al carrito en DB.
        Si el producto ya estaba en DB, suma las cantidades.
        """
        sesion_carrito = request.session.get('carrito', {})
        if not sesion_carrito:
            return  # No hay nada que fusionar

        carrito_db, _ = CarritoDB.objects.get_or_create(usuario=request.user)

        ids = list(sesion_carrito.keys())
        productos = Producto.objects.filter(id__in=ids)

        for producto in productos:
            cantidad_sesion = sesion_carrito[str(producto.id)]

            item, creado = ItemCarrito.objects.get_or_create(
                carrito=carrito_db,
                producto=producto,
                defaults={
                    'cantidad': cantidad_sesion,
                    'precio_unitario': producto.precio,
                }
            )

            if not creado:
                # Ya existía → sumamos las cantidades
                item.cantidad += cantidad_sesion
                item.save()

        # Limpiar la sesión después de fusionar
        request.session['carrito'] = {}

    # ─────────────────────────────────────────────────────────────
    # MÉTODOS PRIVADOS
    # ─────────────────────────────────────────────────────────────

    def _agregar_db(self, producto, cantidad, actualizar):
        item, creado = ItemCarrito.objects.get_or_create(
            carrito=self._carrito_db,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'precio_unitario': producto.precio,   # precio capturado ahora
            }
        )

        if not creado:
            if actualizar:
                if cantidad <= 0:
                    item.delete()
                else:
                    item.cantidad = cantidad
                    item.save()
            else:
                item.cantidad += cantidad
                item.save()

    def _agregar_sesion(self, producto, cantidad, actualizar):
        producto_id = str(producto.id)

        if producto_id not in self._sesion_data:
            self._sesion_data[producto_id] = cantidad
        else:
            if actualizar:
                if cantidad <= 0:
                    del self._sesion_data[producto_id]
                else:
                    self._sesion_data[producto_id] = cantidad
            else:
                self._sesion_data[producto_id] += cantidad

        self._guardar_sesion()

    def _get_items_sesion(self):
        ids = self._sesion_data.keys()
        productos = Producto.objects.filter(id__in=ids).select_related('marca')

        items = []
        for producto in productos:
            cantidad = self._sesion_data[str(producto.id)]
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': producto.precio * cantidad,
            })
        return items

    def _guardar_sesion(self):
        self._sesion.modified = True