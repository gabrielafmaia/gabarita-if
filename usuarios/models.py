from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    avatar = models.ImageField(upload_to="usuarios-avatar/", blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
   
    # Define qual o campo é o nome de usuário
    USERNAME_FIELD = "email"
    # Necessário para createsuperuser continuar funcionando
    REQUIRED_FIELDS = ["username"]
    def __str__(self):
        return self.first_name