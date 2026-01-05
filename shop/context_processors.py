from .models import Categoria

def consulta_categorias(request):        #consulta las categorias desde la DB para renderizarlas en el header.
    categorias = Categoria.objects.all()
    
    return{
        "categorias" : categorias
    }