from django.db import models

class Sobre(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    subtitulo = models.CharField(max_length=200, verbose_name="Subtítulo")
    texto = models.TextField()

    def __str__(self):
        return self.titulo
    

class Membro(models.Model):
    imagem = models.ImageField(upload_to="membros/")
    nome = models.CharField(max_length=50)
    funcao = models.CharField(max_length=200, verbose_name="Função")

    def __str__(self):
        return self.nome
    

class Card(models.Model):
    imagem = models.ImageField(upload_to="cards/")
    titulo = models.CharField(max_length=50, verbose_name="Título")
    texto = models.CharField(max_length=200)

    def __str__(self):
        return self.titulo
