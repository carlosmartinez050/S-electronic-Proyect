
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()  # Retorna CustomUser


# ============================================================================
# TESTS PARA EL MODELO CUSTOMUSER
# ============================================================================

class CustomUserModelTest(TestCase):
    """Tests para el modelo CustomUser"""
    
    def setUp(self):
        """Crear datos de prueba antes de cada test"""
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'password': 'password123'
        }
    
    # ========================================================================
    # TESTS DE CREACIÓN DE USUARIOS
    # ========================================================================
    
    def test_crear_usuario_exitoso(self):
        """Verificar que se puede crear un usuario normal"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        
        # Verificar datos básicos
        self.assertEqual(user.email, 'test@example.com')
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        self.assertEqual(user.first_name, 'Juan')
        self.assertEqual(user.last_name, 'Pérez')
        
        # Verificar que la contraseña está hasheada (NO es texto plano)
        self.assertNotEqual(user.password, 'password123')
        # assertNotEqual(A, B) → Verifica que A sea DIFERENTE de B
        
        self.assertTrue(user.check_password('password123'))
        # assertTrue(X) → Verifica que X sea True
        # check_password() verifica la contraseña hasheada
        
        # Verificar permisos por defecto
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        # assertFalse(X) → Verifica que X sea False
        
        self.assertFalse(user.is_superuser)
    
    def test_crear_superusuario_exitoso(self):
        """Verificar que se puede crear un superusuario"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        # Verificar que tiene todos los permisos
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_crear_usuario_sin_email_falla(self):
        """Verificar que no se puede crear usuario sin email"""
        with self.assertRaises(ValueError):
            # assertRaises(Excepcion) → Verifica que se lance una excepción
            User.objects.create_user(
                email='',  # Email vacío
                password='password123'
            )
    
    def test_email_es_unico(self):
        """Verificar que no se pueden crear dos usuarios con el mismo email"""
        # Crear primer usuario
        User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Intentar crear otro con el mismo email debe fallar
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',  # Email duplicado
                password='password456'
            )
    
    # ========================================================================
    # TESTS DE MÉTODOS DEL MODELO
    # ========================================================================
    
    def test_get_full_name(self):
        """Verificar que get_full_name() retorna nombre completo"""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.assertEqual(user.get_full_name(), 'Juan Pérez')
    
    def test_str_representation(self):
        """Verificar el método __str__"""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez'
        )
        
        # __str__ debe retornar "Juan Pérez (test@example.com)"
        expected = 'Juan Pérez (test@example.com)'
        self.assertEqual(str(user), expected)


# ============================================================================
# RESUMEN
# ============================================================================

"""
TESTS PARA CUSTOMUSER (6 tests):

1. test_crear_usuario_exitoso
   → Verifica creación normal, contraseña hasheada, permisos por defecto

2. test_crear_superusuario_exitoso
   → Verifica que superusuario tiene is_staff=True, is_superuser=True

3. test_crear_usuario_sin_email_falla
   → Verifica que email vacío lanza ValueError

4. test_email_es_unico
   → Verifica constraint de unique=True en email

5. test_get_full_name
   → Verifica método auxiliar

6. test_str_representation
   → Verifica __str__()
"""


#* PARTE 2: FORMULARIOS

from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import RegistroForm, LoginForm

User = get_user_model()


# ============================================================================
# TESTS PARA REGISTROFORM
# ============================================================================

class RegistroFormTest(TestCase):
    """Tests para el formulario de registro"""
    
    # ========================================================================
    # TESTS DE VALIDACIÓN EXITOSA
    # ========================================================================
    
    def test_formulario_valido(self):
        """Verificar que un formulario completo y correcto es válido"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        }
        
        form = RegistroForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        # assertTrue(X) → Verifica que X sea True
        # Un formulario válido debe retornar True
    
    # ========================================================================
    # TESTS DE VALIDACIÓN FALLIDA
    # ========================================================================
    
    def test_email_duplicado_no_valido(self):
        """Verificar que no se puede registrar email ya existente"""
        # Crear usuario con un email
        User.objects.create_user(
            email='juan@example.com',
            password='password123'
        )
        
        # Intentar registrar otro con el mismo email
        form_data = {
            'first_name': 'Pedro',
            'last_name': 'García',
            'email': 'juan@example.com',  # Email duplicado
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        }
        
        form = RegistroForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        # assertFalse(X) → Verifica que X sea False
        
        self.assertIn('email', form.errors)
        # assertIn(item, contenedor) → Verifica que 'item' ESTÁ en 'contenedor'
        # Debe haber un error en el campo 'email'
    
    def test_passwords_no_coinciden(self):
        """Verificar que contraseñas diferentes generan error"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'DiferenteContraseña456',  # No coincide
        }
        
        form = RegistroForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        # El error debe estar en password2
    
    def test_campos_requeridos(self):
        """Verificar que campos vacíos generan error"""
        form = RegistroForm(data={})
        
        self.assertFalse(form.is_valid())
        
        # Verificar que hay errores en todos los campos requeridos
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
    
    # ========================================================================
    # TESTS DE GUARDADO
    # ========================================================================
    
    def test_guardar_usuario(self):
        """Verificar que save() crea el usuario correctamente"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        }
        
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Guardar usuario
        user = form.save()
        
        # Verificar que el usuario existe en la DB
        self.assertEqual(User.objects.count(), 1)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        # Verificar datos
        self.assertEqual(user.email, 'juan@example.com')
        self.assertEqual(user.first_name, 'Juan')
        
        # Verificar que la contraseña está hasheada
        self.assertTrue(user.check_password('ContraseñaSegura123'))


# ============================================================================
# TESTS PARA LOGINFORM
# ============================================================================

class LoginFormTest(TestCase):
    """Tests para el formulario de login"""
    
    def setUp(self):
        """Crear usuario de prueba antes de cada test"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
    
    # ========================================================================
    # TESTS DE VALIDACIÓN
    # ========================================================================
    
    def test_login_valido(self):
        """Verificar que credenciales correctas son válidas"""
        # LoginForm hereda de AuthenticationForm, necesita request=None
        form = LoginForm(data={
            'username': 'test@example.com',  # username es el email
            'password': 'password123'
        })
        
        self.assertTrue(form.is_valid())
    
    def test_email_invalido(self):
        """Verificar que email incorrecto genera error"""
        form = LoginForm(data={
            'username': 'noexiste@example.com',
            'password': 'password123'
        })
        
        self.assertFalse(form.is_valid())
    
    def test_password_invalido(self):
        """Verificar que contraseña incorrecta genera error"""
        form = LoginForm(data={
            'username': 'test@example.com',
            'password': 'contraseñaincorrecta'
        })
        
        self.assertFalse(form.is_valid())


# ============================================================================
# RESUMEN
# ============================================================================

"""
TESTS PARA FORMULARIOS (8 tests):

REGISTROFORM (5 tests):
1. test_formulario_valido
   → Datos correctos → is_valid() = True

2. test_email_duplicado_no_valido
   → Email ya registrado → error en campo 'email'

3. test_passwords_no_coinciden
   → password1 != password2 → error en 'password2'

4. test_campos_requeridos
   → Formulario vacío → errores en todos los campos

5. test_guardar_usuario
   → form.save() crea usuario con contraseña hasheada

LOGINFORM (3 tests):
6. test_login_valido
   → Credenciales correctas → is_valid() = True

7. test_email_invalido
   → Email no existe → is_valid() = False

8. test_password_invalido
   → Contraseña incorrecta → is_valid() = False
"""


#* PARTE 3: VISTA DE REGISTRO

# ============================================================================
# TESTS PARA VISTA DE REGISTRO
# ============================================================================
 
class RegistroViewTest(TestCase):
    """Tests para la vista de registro (registro_view)"""
    
    def setUp(self):
        """Configurar cliente HTTP antes de cada test"""
        self.client = Client()
        self.url = reverse('accounts:registro')
    
    # ========================================================================
    # TESTS GET - MOSTRAR FORMULARIO
    # ========================================================================
    
    def test_get_muestra_formulario(self):
        """Verificar que GET muestra el formulario de registro"""
        response = self.client.get(self.url)
        
        # Verificar código 200 OK
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        # Verificar que usa el template correcto
        self.assertTemplateUsed(response, 'accounts/registro.html')
        # assertTemplateUsed → Verifica que se renderizó ese template
        
        # Verificar que el formulario está en el contexto
        self.assertIn('form', response.context)
        # assertIn(item, dict) → Verifica que 'form' está en el contexto
    
    # ========================================================================
    # TESTS POST - REGISTRO EXITOSO
    # ========================================================================
    
    def test_post_registro_exitoso(self):
        """Verificar que POST con datos válidos crea usuario y loguea"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Verificar que redirige (código 302)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que redirige al home
        self.assertRedirects(response, reverse('shop:home'))
        # assertRedirects(response, url) → Verifica la redirección
        
        # Verificar que el usuario fue creado
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, 'juan@example.com')
        
        # Verificar que el usuario está logueado automáticamente
        # (esto lo hace la vista con login(request, user))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # assertTrue(X) → Verifica que X sea True
    
    # ========================================================================
    # TESTS POST - REGISTRO FALLIDO
    # ========================================================================
    
    def test_post_email_duplicado(self):
        """Verificar que email duplicado muestra error"""
        # Crear usuario existente
        User.objects.create_user(
            email='juan@example.com',
            password='password123'
        )
        
        # Intentar registrar con el mismo email
        form_data = {
            'first_name': 'Pedro',
            'last_name': 'García',
            'email': 'juan@example.com',  # Email duplicado
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # NO debe redirigir (se queda en la misma página)
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el formulario tiene errores
        self.assertFalse(response.context['form'].is_valid())
        # assertFalse(X) → Verifica que X sea False
        
        # Verificar que NO se creó otro usuario
        self.assertEqual(User.objects.count(), 1)
    
    def test_post_passwords_no_coinciden(self):
        """Verificar que contraseñas diferentes muestran error"""
        form_data = {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@example.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'DiferenteContraseña456',  # No coincide
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # NO debe crear el usuario
        self.assertEqual(User.objects.count(), 0)
        
        # Se queda en la página de registro
        self.assertEqual(response.status_code, 200)
        
        # El formulario tiene errores
        self.assertFalse(response.context['form'].is_valid())
    
    def test_post_campos_vacios(self):
        """Verificar que campos vacíos muestran error"""
        response = self.client.post(self.url, data={})
        
        # NO debe crear usuario
        self.assertEqual(User.objects.count(), 0)
        
        # Formulario tiene errores
        self.assertFalse(response.context['form'].is_valid())
    
    # ========================================================================
    # TESTS DE REDIRECCIÓN SI YA ESTÁ LOGUEADO
    # ========================================================================
    
    def test_usuario_logueado_redirige_al_home(self):
        """Verificar que usuario logueado no puede acceder a registro"""
        # Crear y loguear usuario
        user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.client.login(username='test@example.com', password='password123')
        
        # Intentar acceder a registro
        response = self.client.get(self.url)
        
        # Debe redirigir al home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:home'))
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA VISTA DE REGISTRO (7 tests):
 
GET (1 test):
1. test_get_muestra_formulario
   → GET retorna 200, template correcto, formulario en contexto
 
POST EXITOSO (1 test):
2. test_post_registro_exitoso
   → Datos válidos → usuario creado + logueado + redirige
 
POST FALLIDO (4 tests):
3. test_post_email_duplicado
   → Email existente → error, no crea usuario
 
4. test_post_passwords_no_coinciden
   → password1 != password2 → error, no crea usuario
 
5. test_post_campos_vacios
   → Formulario vacío → error
 
6. test_post_campos_vacios
   → Verifica que formulario vacío tiene errores
 
SEGURIDAD (1 test):
7. test_usuario_logueado_redirige_al_home
   → Usuario ya logueado → redirige al home (no puede registrarse de nuevo)
"""
 

#* PARTE 4: VISTA DE LOGIN

# ============================================================================
# TESTS PARA VISTA DE LOGIN
# ============================================================================
 
class LoginViewTest(TestCase):
    """Tests para la vista de login (login_view)"""
    
    def setUp(self):
        """Configurar datos de prueba antes de cada test"""
        self.client = Client()
        self.url = reverse('accounts:login')
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
    
    # ========================================================================
    # TESTS GET - MOSTRAR FORMULARIO
    # ========================================================================
    
    def test_get_muestra_formulario(self):
        """Verificar que GET muestra el formulario de login"""
        response = self.client.get(self.url)
        
        # Verificar código 200 OK
        self.assertEqual(response.status_code, 200)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        # Verificar template correcto
        self.assertTemplateUsed(response, 'accounts/login.html')
        
        # Verificar que el formulario está en el contexto
        self.assertIn('form', response.context)
    
    # ========================================================================
    # TESTS POST - LOGIN EXITOSO
    # ========================================================================
    
    def test_post_login_exitoso(self):
        """Verificar que credenciales correctas loguean al usuario"""
        form_data = {
            'username': 'test@example.com',  # username = email
            'password': 'password123'
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Verificar que redirige (código 302)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que redirige al home
        self.assertRedirects(response, reverse('shop:home'))
        
        # Verificar que el usuario está logueado
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # assertTrue(X) → Verifica que X sea True
        
        # Verificar que es el usuario correcto
        self.assertEqual(response.wsgi_request.user.email, 'test@example.com')
    
    def test_post_login_con_parametro_next(self):
        """Verificar que redirige a 'next' si viene en URL"""
        # Simular: usuario intentó acceder a /mi-cuenta/ pero no estaba logueado
        # Django lo redirigió a /login/?next=/mi-cuenta/
        url_with_next = f"{self.url}?next=/producto/test-slug/"
        
        form_data = {
            'username': 'test@example.com',
            'password': 'password123'
        }
        
        response = self.client.post(url_with_next, data=form_data)
        
        # Debe redirigir a la URL que estaba en 'next'
        self.assertRedirects(response, '/producto/test-slug/', 
                            fetch_redirect_response=False)
        # fetch_redirect_response=False → No seguir la redirección
    
    # ========================================================================
    # TESTS POST - LOGIN FALLIDO
    # ========================================================================
    
    def test_post_email_incorrecto(self):
        """Verificar que email incorrecto no loguea"""
        form_data = {
            'username': 'noexiste@example.com',  # Email que no existe
            'password': 'password123'
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # NO debe redirigir (se queda en login)
        self.assertEqual(response.status_code, 200)
        
        # Verificar que NO está logueado
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        # assertFalse(X) → Verifica que X sea False
        
        # Verificar que el formulario tiene errores
        self.assertFalse(response.context['form'].is_valid())
    
    def test_post_password_incorrecto(self):
        """Verificar que contraseña incorrecta no loguea"""
        form_data = {
            'username': 'test@example.com',
            'password': 'contraseñaincorrecta'  # Password incorrecto
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # NO loguea
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Formulario tiene errores
        self.assertFalse(response.context['form'].is_valid())
    
    # ========================================================================
    # TESTS DE REDIRECCIÓN SI YA ESTÁ LOGUEADO
    # ========================================================================
    
    def test_usuario_logueado_redirige_al_home(self):
        """Verificar que usuario logueado no puede acceder a login"""
        # Loguear usuario
        self.client.login(username='test@example.com', password='password123')
        
        # Intentar acceder a login
        response = self.client.get(self.url)
        
        # Debe redirigir al home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:home'))
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA VISTA DE LOGIN (6 tests):
 
GET (1 test):
1. test_get_muestra_formulario
   → GET retorna 200, template correcto, formulario en contexto
 
POST EXITOSO (2 tests):
2. test_post_login_exitoso
   → Credenciales correctas → loguea + redirige al home
 
3. test_post_login_con_parametro_next
   → Si viene ?next=/url/ → redirige a esa URL
 
POST FALLIDO (2 tests):
4. test_post_email_incorrecto
   → Email no existe → no loguea, muestra errores
 
5. test_post_password_incorrecto
   → Contraseña incorrecta → no loguea, muestra errores
 
SEGURIDAD (1 test):
6. test_usuario_logueado_redirige_al_home
   → Usuario ya logueado → redirige (no puede volver a login)
"""

#* PARTE 5: VISTA DE LOGOUT

# ============================================================================
# TESTS PARA VISTA DE LOGOUT
# ============================================================================
 
class LogoutViewTest(TestCase):
    """Tests para la vista de logout (logout_view)"""
    
    def setUp(self):
        """Configurar datos de prueba antes de cada test"""
        self.client = Client()
        self.url = reverse('accounts:logout')
        
        # Crear y loguear usuario
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.client.login(username='test@example.com', password='password123')
    
    # ========================================================================
    # TESTS POST - LOGOUT EXITOSO
    # ========================================================================
    
    def test_post_logout_exitoso(self):
        """Verificar que POST cierra sesión correctamente"""
        # Verificar que está logueado antes
        response_before = self.client.get(reverse('shop:home'))
        self.assertTrue(response_before.wsgi_request.user.is_authenticated)
        # assertTrue(X) → Verifica que X sea True
        
        # Hacer logout con POST
        response = self.client.post(self.url)
        
        # Verificar que redirige (código 302)
        self.assertEqual(response.status_code, 302)
        # assertEqual(A, B) → Verifica que A sea IGUAL a B
        
        # Verificar que redirige a login
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Verificar que el usuario ya NO está logueado
        response_after = self.client.get(reverse('shop:home'))
        self.assertFalse(response_after.wsgi_request.user.is_authenticated)
        # assertFalse(X) → Verifica que X sea False
    
    # ========================================================================
    # TESTS GET - RECHAZAR LOGOUT POR GET
    # ========================================================================
    
    def test_get_logout_redirige_sin_cerrar_sesion(self):
        """Verificar que GET no cierra sesión (seguridad contra CSRF)"""
        # Intentar logout con GET (inseguro)
        response = self.client.get(self.url)
        
        # Redirige al home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:home'))
        
        # Pero NO cierra sesión (el usuario sigue logueado)
        response_check = self.client.get(reverse('shop:home'))
        self.assertTrue(response_check.wsgi_request.user.is_authenticated)
        # ↑ Importante: previene ataques CSRF donde alguien pone
        # <img src="/logout/"> en un sitio malicioso
    
    # ========================================================================
    # TESTS DE PROTECCIÓN @login_required
    # ========================================================================
    
    def test_logout_requiere_autenticacion(self):
        """Verificar que solo usuarios logueados pueden hacer logout"""
        # Primero hacer logout
        self.client.post(self.url)
        
        # Intentar hacer logout de nuevo (sin estar logueado)
        response = self.client.post(self.url)
        
        # Debe redirigir a login (por @login_required)
        self.assertEqual(response.status_code, 302)
        # La URL debe contener /login/ y ?next=/logout/
        self.assertIn('/login/', response.url)
        # assertIn(item, string) → Verifica que '/login/' está en la URL
 
 
# ============================================================================
# RESUMEN
# ============================================================================
 
"""
TESTS PARA VISTA DE LOGOUT (3 tests):
 
POST EXITOSO (1 test):
1. test_post_logout_exitoso
   → POST → cierra sesión + redirige a login
 
SEGURIDAD - RECHAZAR GET (1 test):
2. test_get_logout_redirige_sin_cerrar_sesion
   → GET → redirige pero NO cierra sesión
   → Previene CSRF (Cross-Site Request Forgery)
 
PROTECCIÓN @login_required (1 test):
3. test_logout_requiere_autenticacion
   → Usuario no logueado → redirige a login
 
---
 
¿POR QUÉ RECHAZAR LOGOUT POR GET?
 
Imagina que alguien crea esta página maliciosa:
```html
<img src="https://tu-tienda.com/logout/">
```
 
Si aceptaras GET, cualquier usuario logueado que visite esa página
se cerraría su sesión automáticamente (sin querer).
 
Por eso SOLO aceptamos POST → requiere un formulario → más seguro.
"""
  