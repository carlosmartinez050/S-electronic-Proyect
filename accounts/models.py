 # Create your models here.

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado que usa EMAIL en vez de username
    para crear usuarios y superusuarios.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hashea la contraseña automáticamente
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Usuario personalizado que usa EMAIL como identificador
    en lugar del username por defecto de Django.
    """

    username = None

    email = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico',
        help_text='Será usado para iniciar sesión'
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name='Nombre'
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name='Apellido'
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name='Fecha de registro'
    )

    # Asignar nuestro manager personalizado
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"