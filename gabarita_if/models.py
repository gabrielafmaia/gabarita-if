from django.db import models
from django.conf import settings
from tinymce import models as tinymce_models

class Disciplina(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Assunto(models.Model):
    nome = models.CharField(max_length=50)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Questao(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    assunto = models.ForeignKey(Assunto, on_delete=models.PROTECT)
    enunciado = tinymce_models.HTMLField()
    imagem = models.ImageField(upload_to="imagens-das-questoes/", blank=True, null=True)
    gabarito_comentado = tinymce_models.HTMLField()
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


class Avaliacao(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    ano = models.PositiveIntegerField()
    questoes = models.ManyToManyField(Questao, verbose_name="Questões")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.titulo} ({self.ano})"


class Prova(Avaliacao):
    instituicao = models.CharField(max_length=10, verbose_name="Instituição", blank=True, null=True)


class Simulado(Avaliacao):
    subtitulo = models.CharField(max_length=50, verbose_name="Subtítulo")


class TextoApoio(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    texto = tinymce_models.HTMLField(blank=True, null=True)
    imagem = models.ImageField(upload_to="textos-de-apoio/", blank=True, null=True)
    questoes = models.ManyToManyField(Questao, verbose_name="Questões")
    
    class Meta:
        verbose_name = "Texto de Apoio"
        verbose_name_plural = "Textos de Apoio"

    def __str__(self):
        return self.titulo


class Caderno(models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questoes = models.ManyToManyField(Questao, verbose_name="Questões")
    cor = models.CharField(max_length=7, default="#4cc49e")

    def __str__(self):
        return self.nome
    
    @property
    def total_questoes(self):
        return self.questoes.count()

    @property
    def total_assuntos(self):
        return self.questoes.values("assunto").distinct().count()

    @property
    def questoes_resolvidas(self):
        return (self.questoes.filter(respostas__usuario=self.usuario).distinct().count())


class RespostaUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name="respostas")
    alternativa_escolhida = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
    acertou = models.BooleanField()
    simulado = models.ForeignKey(Simulado, on_delete=models.SET_NULL, blank=True, null=True)
    prova = models.ForeignKey(Prova, on_delete=models.SET_NULL, blank=True, null=True)
    respondido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resposta do Usuário"
        verbose_name_plural = "Respostas dos Usuários"

    def __str__(self):
        return f"{self.usuario} - Questão {self.questao.id} ({self.alternativa_escolhida})"