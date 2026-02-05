from .models import Categoria

# Context processors para pasar las categorías a todas las plantillas, osea a todo el sitio.

def consulta_categorias(request):        #consulta las categorias desde la DB para renderizarlas en el header.
    categorias = Categoria.objects.all()
    
    return{
        "categorias" : categorias
    }