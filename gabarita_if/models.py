from django.db import models
from django.conf import settings


class Disciplina(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome


class Assunto(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class ListaPDF(models.Model):
    assunto = models.ForeignKey(Assunto, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='listas-pdf/')


class Avaliacao(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    ano = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.titulo} ({self.ano})"

    class Meta:
        abstract = True


class Prova(Avaliacao):
    instituicao = models.CharField(max_length=100, verbose_name="Instituição")


class Simulado(Avaliacao):
    subtitulo = models.CharField(max_length=50, verbose_name="Subtítulo")


class TextoDeApoio(models.Model):
    titulo = models.CharField(max_length=50, unique=True, verbose_name="Título")
    texto = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='textos-de-apoio/', blank=True, null=True)

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Texto de Apoio"
        verbose_name_plural = "Textos de Apoio"


class Questao(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    assunto = models.ForeignKey(Assunto, on_delete=models.PROTECT)
    texto = models.TextField()
    gabarito_comentado = models.TextField(verbose_name="Gabarito Comentado")
    video_solucao = models.FileField(upload_to='videos-solucao/', blank=True, verbose_name="Vídeo Solução")
    texto_de_apoio = models.ForeignKey(TextoDeApoio, on_delete=models.SET, blank=True, null=True, verbose_name="Texto de Apoio")
    prova = models.ForeignKey(Prova, on_delete=models.SET, null=True, blank=True)
    simulado = models.ForeignKey(Simulado, on_delete=models.SET, null=True, blank=True)

    def __str__(self):
        return self.texto
    
    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"


class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    texto = models.CharField(max_length=2000)
    correta = models.BooleanField(verbose_name="Esta é a alternativa correta?")

    def __str__(self):
        return self.texto


class ListaPersonalizada(models.Model):
    nome = models.CharField(max_length=100)
    criada_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Listas Personalizadas"


class Filtro(models.Model):
    nome = models.CharField(max_length=200)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET, null=True, blank=True)
    assunto = models.ForeignKey(Assunto, on_delete=models.SET, null=True, blank=True)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Comentario(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Comentário"