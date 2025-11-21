from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    avatar = models.ImageField(upload_to="avatar-dos-usuarios/", blank=True, null=True, verbose_name="Foto de Perfil")
    email = models.EmailField(max_length=255, unique=True, verbose_name="E-mail")
    first_name = models.CharField(max_length=150, verbose_name="Nome")
    last_name = models.CharField(max_length=150, verbose_name="Sobrenome")
   
    # Define qual o campo é o nome de usuário
    USERNAME_FIELD = "email"
    # Necessário para createsuperuser continuar funcionando
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.first_name