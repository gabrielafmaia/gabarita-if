from django.db import models
from django.conf import settings
from django.db.models import Q, UniqueConstraint


class Disciplina(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome


class Assunto(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Avaliacao(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    ano = models.PositiveIntegerField()

    def __str__(self):
        return self.titulo

    class Meta:
        abstract = True
 

class Prova(Avaliacao):
    instituicao = models.CharField(max_length=100, verbose_name="Instituição")


class Simulado(Avaliacao):
    subtitulo = models.CharField(max_length=50, verbose_name="Subtítulo")


class TextoDeApoio(models.Model):
    titulo = models.CharField(max_length=50, unique=True, verbose_name="Título")
    texto = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to="textos-de-apoio/", blank=True, null=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Texto de Apoio"
        verbose_name_plural = "Textos de Apoio"


class Questao(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    assunto = models.ForeignKey(Assunto, on_delete=models.PROTECT)
    prova = models.ForeignKey(Prova, on_delete=models.SET, blank=True, null=True)
    simulado = models.ForeignKey(Simulado, on_delete=models.SET, blank=True, null=True)
    texto_de_apoio = models.ManyToManyField(TextoDeApoio, blank=True, verbose_name="Textos de apoio")
    enunciado = models.TextField()
    gabarito_comentado = models.TextField()
    video_solucao = models.URLField(max_length=500, blank=True, null=True, verbose_name="Vídeo solução")
    alternativa_a = models.TextField(verbose_name="Alternativa A")
    alternativa_b = models.TextField(verbose_name="Alternativa B") 
    alternativa_c = models.TextField(verbose_name="Alternativa C")
    alternativa_d = models.TextField(verbose_name="Alternativa D")
    alternativa_correta = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])

    def __str__(self):
        return self.enunciado
    
    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"
        constraints = [
            UniqueConstraint(
                fields=['prova', 'simulado'],
                condition=Q(prova__isnull=False) & Q(simulado__isnull=False),
                name='prova_or_simulado_not_both'
            )
        ]


class ListaPersonalizada(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questao = models.ManyToManyField(Questao, blank=True, verbose_name="Questões")
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=7, default="#4cc49e")

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Listas Personalizadas"


class Comentario(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Comentário"