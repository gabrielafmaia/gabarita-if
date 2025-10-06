from django.db import models

class About(models.Model):
    title = models.CharField(max_length=50, verbose_name="Título")
    subtitle = models.CharField(max_length=200, verbose_name="Subtítulo")
    text = models.TextField(verbose_name="Texto")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name="Sobre"

class Member(models.Model):
    image = models.ImageField(null=False, blank=False, upload_to="members_images/", verbose_name="Imagem")
    name = models.CharField(max_length=50, verbose_name="Nome")
    occupation = models.CharField(max_length=200, verbose_name="Ocupação")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name="Membro"

class Card(models.Model):
    image = models.ImageField(null=False, blank=False, upload_to="cards_images/", verbose_name="Imagem")
    title = models.CharField(max_length=50, verbose_name="Título")
    text = models.CharField(max_length=200, verbose_name="Texto")

    def __str__(self):
        return self.title
