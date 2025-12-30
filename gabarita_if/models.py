from django.db import models
import random
from django.conf import settings
from tinymce import models as tinymce_models
from django.utils.html import strip_tags


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


class Fonte(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]
    
    def __str__(self):
        return self.nome


class Questao(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT)
    assunto = models.ForeignKey(Assunto, on_delete=models.PROTECT)
    fonte = models.ForeignKey(Fonte, on_delete=models.PROTECT)
    dificuldade = models.CharField(max_length=10, choices=[("Fácil", "Fácil"), ("Média", "Média"), ("Difícil", "Difícil")])
    enunciado = tinymce_models.HTMLField()
    codigo = models.CharField(max_length=6, unique=True, editable=False, null=True, blank=True, verbose_name="Código")
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
        enunciado = strip_tags(self.enunciado) # Remove o HTML do enunciado antes de retornar
        return enunciado[:50]

    @classmethod
    def _generate_unique_codigo(cls):
        while True:
            codigo = str(random.randint(0, 999999)).zfill(6)
            if not cls.objects.filter(codigo=codigo).exists():
                return codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generate_unique_codigo()
        super().save(*args, **kwargs)
    
    @property
    def alternativas(self):
        return {
            "A": self.alternativa_a,
            "B": self.alternativa_b,
            "C": self.alternativa_c,
            "D": self.alternativa_d,
        }


class Comentario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    texto = tinymce_models.HTMLField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def __str__(self):
        return f"{self.usuario} - Questão {self.questao.id}"


class Avaliacao(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    subtitulo = models.CharField(max_length=50, verbose_name="Subtítulo", blank=True, null=True)
    fonte = models.ForeignKey(Fonte, on_delete=models.CASCADE)
    ano = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=[("Prova", "Prova"), ("Simulado", "Simulado")])
    questoes = models.ManyToManyField(Questao, verbose_name="Questões")

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"

    def __str__(self):
        return f"{self.titulo} ({self.ano})"


class TextoApoio(models.Model):
    titulo = models.CharField(max_length=50, verbose_name="Título")
    texto = tinymce_models.HTMLField(blank=True, null=True)
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
    cor = models.CharField(max_length=7, default="#fff")

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


class RespostaAvaliacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, null=True, blank=True)
    finalizada = models.BooleanField()
    
    class Meta:
        verbose_name = "Resposta da Avaliação"
        verbose_name_plural = "Respostas das Avaliações"

    def __str__(self):
        avaliacao = self.avaliacao
        return f"{self.usuario} - {avaliacao}"


class RespostaQuestao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name="respostas")
    alternativa_escolhida = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
    acertou = models.BooleanField()
    tentativa = models.ForeignKey(RespostaAvaliacao, on_delete=models.CASCADE, null=True, blank=True)
    respondida_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resposta da Questão"
        verbose_name_plural = "Respostas das Questões"

    def __str__(self):
        return f"{self.usuario} - Questão {self.questao.id} ({self.alternativa_escolhida})"