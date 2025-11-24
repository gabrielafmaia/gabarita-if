from django.db import models
from django.conf import settings


class Disciplina(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Assunto(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Avaliacao(models.Model):
    ano = models.PositiveIntegerField()
    titulo = models.CharField(max_length=50, verbose_name="Título")

    class Meta:
        abstract = True
        ordering = ["ano"]

    def __str__(self):
        return f"{self.titulo} ({self.ano})"


class Prova(Avaliacao):
    instituicao = models.CharField(max_length=10, verbose_name="Instituição")


class Simulado(Avaliacao):
    subtitulo = models.CharField(max_length=50, verbose_name="Subtítulo")


class Questao(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    assunto = models.ForeignKey(Assunto, on_delete=models.PROTECT)
    prova = models.ForeignKey(Prova, on_delete=models.SET_NULL, blank=True, null=True)
    simulados = models.ManyToManyField(Simulado, blank=True)
    enunciado = models.TextField()
    imagem = models.ImageField(upload_to="imagens-das-questoes/", blank=True, null=True)
    gabarito_comentado = models.TextField()
    video_solucao = models.URLField(max_length=500, blank=True, null=True, verbose_name="Vídeo solução")
    alternativa_a = models.CharField(max_length=500, verbose_name="Alternativa A")
    alternativa_b = models.CharField(max_length=500, verbose_name="Alternativa B") 
    alternativa_c = models.CharField(max_length=500, verbose_name="Alternativa C")
    alternativa_d = models.CharField(max_length=500, verbose_name="Alternativa D")
    alternativa_correta = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])

    class Meta:
            verbose_name = "Questão"
            verbose_name_plural = "Questões"
    
    def __str__(self):
        return self.enunciado[:50]
    
    @property
    def alternativas(self):
        return {
            "A": self.alternativa_a,
            "B": self.alternativa_b,
            "C": self.alternativa_c,
            "D": self.alternativa_d,
        }


class TextoDeApoio(models.Model):
    prova = models.ForeignKey(Prova, on_delete=models.SET_NULL, blank=True, null=True)
    simulados = models.ManyToManyField(Simulado, blank=True)
    questoes = models.ManyToManyField(Questao, verbose_name="Questões", blank=True)
    titulo = models.CharField(max_length=50, verbose_name="Título")
    texto = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to="textos-de-apoio/", blank=True, null=True)
    
    class Meta:
        verbose_name = "Texto de Apoio"
        verbose_name_plural = "Textos de Apoio"

    def __str__(self):
        return self.titulo


class ListaPersonalizada(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questoes = models.ManyToManyField(Questao, verbose_name="Questões")
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=7, default="#4cc49e")

    class Meta:
        verbose_name_plural = "Listas Personalizadas"

    def __str__(self):
        return self.nome
