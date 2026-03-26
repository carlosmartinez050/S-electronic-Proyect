# accounts/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()  # Retorna tu CustomUser


class EmailBackend(ModelBackend):
    """
    Autenticación por email en vez de username.
    Django llamará a este backend cuando alguien intente loguearse.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Django pasa el email en el parámetro 'username' por convención
        email = username

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # No revelar si el email existe o no — seguridad
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None