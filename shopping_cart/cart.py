from shop.models import Producto

class Carrito:
    
    def __init__(self, request):
        self.session = request.session
        self._carrito = self.session.get('carrito')
        
        if self._carrito is None:  # Si no existía
            self._carrito = {}
            self.session['carrito'] = self._carrito  # lo creamos en sesión
            
    # -----------------------------------------------------------------------------
    def _guardar (self):
        self.session.modified = True
        
    # -----------------------------------------------------------------------------
    def agregar(self, producto, cantidad=1, actualizar=False):
        producto_id = str(producto.id)  # convertimos el id a string
        
        if producto.stock <= 0:
            return
        if producto_id not in self._carrito:
            self._carrito[producto_id] = cantidad
        else:
            if actualizar:
              self._carrito[producto_id] = cantidad   
            else:
                self._carrito[producto_id] += cantidad
                
        self._guardar()
        
    #--------------------------------------------------------------------------------
    def eliminar(self, producto):
        producto_id = str(producto.id)
        
        if producto_id in self._carrito:
            del self._carrito[producto_id]
            
        self._guardar()
    
    #------------------------------------------------------------------------------
    def limpiar(self):
        self.session['carrito'] = {}    # vacía en la sesión
        self._carrito = {}              # vacía en memoria
        self._guardar()                 # avisa a Django
    
    #-------------------------------------------------------------------------------
    def get_items(self):
        ids = self._carrito.keys()
    
        productos = Producto.objects.filter(id__in=ids)
    
        items = []
        for producto in productos:
            cantidad = self._carrito[str(producto.id)]
            subtotal = producto.precio * cantidad
        
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })
    
        return items
    
    #--------------------------------------------------------------------------------
    def total_articulos(self):
        return sum(self._carrito.values())
        
        
    #---------------------------------------------------------------------------------    
    def total_precio(self):
       return sum(item['subtotal'] for item in self.get_items()) 
   
    #---------------------------------------------------------------------------
    def esta_vacio(self):
        return len(self._carrito) == 0