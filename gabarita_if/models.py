from django.db import models
from django.conf import settings

class Disciplina(models.Model):
    DISCIPLINAS = [
        ("PORTUGUES", "Português"),
        ("MATEMATICA", "Matemática"),
    ]

    nome = models.CharField(max_length=20, choices=DISCIPLINAS, unique=True)

    def __str__(self):
        return self.get_nome_display()

class Assunto(models.Model):
    ASSUNTOS_PORTUGUES = [
        ("TIPOLOGIA_GENEROS", "Tipologia e Gêneros Textuais"),
    ]

    ASSUNTOS_MATEMATICA = [
        ("SISTEMA_NUMERACAO", "Sistema de Numeração"),
    ]

    TODOS_ASSUNTOS = ASSUNTOS_PORTUGUES + ASSUNTOS_MATEMATICA

    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, choices=TODOS_ASSUNTOS)

    def __str__(self):
        return self.get_nome_display()

class Avaliacao(models.Model):
    PROVA = "PROVA"
    SIMULADO = "SIMULADO"

    AVALIACOES = [
        (PROVA, "Prova"),
        (SIMULADO, "Simulado"),
    ]

    titulo = models.CharField(max_length=50, verbose_name="Título")
    tipo = models.CharField(max_length=10, choices=AVALIACOES)
    ano = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.titulo} ({self.ano})"

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

class TextoDeApoio(models.Model):
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
    gabarito_comentado = models.TextField()
    video_solucao = models.FileField(upload_to='videos-solucao/', blank=True, verbose_name="Vídeo Solução")
    texto_de_apoio = models.ForeignKey(TextoDeApoio, on_delete=models.SET, blank=True,)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.SET, verbose_name="Avaliação")

    def __str__(self):
        return self.texto
    
    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    texto = models.CharField(max_length=2000)
    correta = models.BooleanField(default=False, verbose_name="Esta é a alternativa correta?")

    def __str__(self):
        return self.texto

class ListaPersonalizada(models.Model):
    nome = models.CharField(max_length=100)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Listas Personalizadas"

class Filtro(models.Model):
    nome = models.CharField(max_length=200)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET, null=True, blank=True)
    assunto = models.ForeignKey(Assunto, on_delete=models.SET, null=True, blank=True)
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.texto

class Comentario(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Comentário"