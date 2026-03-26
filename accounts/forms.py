
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistroForm(forms.ModelForm):
    """
    Formulario de registro de nuevos usuarios.
    Incluye validación de contraseña y confirmación.
    """

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-input',
            'autocomplete': 'new-password'
        })
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite tu contraseña',
            'class': 'form-input',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Nombre',
                'class': 'form-input',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Apellido',
                'class': 'form-input',
                'autocomplete': 'family-name'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Correo electrónico',
                'class': 'form-input',
                'autocomplete': 'email' 
            }),
        }

    def clean_email(self):
        """Verificar que el email no esté registrado"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        """Verificar que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError({'password2': 'Las contraseñas no coinciden.'})

        return cleaned_data

    def save(self, commit=True):
        """Guardar usuario con contraseña hasheada"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Formulario de login.
    Extiende AuthenticationForm de Django — ya incluye
    validación de credenciales y protección contra fuerza bruta.
    """

    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-input',
            'autocomplete': 'email', 
            'autofocus': True
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-input',
            'autocomplete': 'current-password'
        })
    )