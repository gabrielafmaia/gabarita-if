from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from .models import Usuario

class CadastroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "email"]

class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "avatar", "curso"]

class UsuarioChangeForm(UserChangeForm):
    password = None
    
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "avatar", "curso"]