from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Usuario


class CadastroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "email"]


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "avatar", "is_active"]


class UsuarioChangeForm(UserChangeForm):
    password = None
    
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "avatar", "is_active"]