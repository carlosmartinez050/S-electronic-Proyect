
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm
from shopping_cart.cart import Carrito


def registro_view(request):
    """
    Vista de registro de nuevos usuarios.
    GET  → muestra el formulario vacío
    POST → valida y crea el usuario
    """
    # Si ya está logueado, no tiene sentido registrarse
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Logueamos al usuario automáticamente después del registro
            login(request, user, backend='accounts.backend.EmailBackend')
            
            
            Carrito.fusionar_sesion_a_db(request)
            
            messages.success(request, f'¡Bienvenido, {user.first_name}!')
            return redirect('shop:home')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = RegistroForm()

    return render(request, 'accounts/registro.html', {'form': form})


def login_view(request):
    """
    Vista de login.
    GET  → muestra el formulario
    POST → valida credenciales y loguea
    """
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            Carrito.fusionar_sesion_a_db(request)
            
            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name}!')

            # Redirección según rol     #!COMENTADA HASTA DESARROLLAR EL ADMIN PANEL
            # if user.is_staff:
            #     return redirect('admin_panel:dashboard')

            # Si venía de una página protegida, volver a ella
            next_url = request.GET.get('next', 'shop:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Vista de logout.
    Solo acepta POST — nunca logout por GET, es una vulnerabilidad.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Sesión cerrada correctamente.')
        return redirect('accounts:login')

    # Si alguien intenta hacer GET, lo mandamos al home
    return redirect('shop:home')