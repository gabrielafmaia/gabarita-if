from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to="usuarios-avatar/", blank=True, null=True)

    def __str__(self):
        return self.first_name