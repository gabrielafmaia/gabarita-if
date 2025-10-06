from django.db import models
from django.conf import settings

class Subject(models.Model):
    PORTUGUESE = "PORTUGUES"
    MATH = "MATEMATICA"

    SUBJECT_CHOICES = [
        (PORTUGUESE, "Português"),
        (MATH, "Matemática"),
    ]

    name = models.CharField(max_length=20, choices=SUBJECT_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    TIPOLOGIA_GENEROS = "TIPOLOGIA_GENEROS"
    PORTUGUESE_TOPICS = [
        (TIPOLOGIA_GENEROS, "Tipologia e Gêneros Textuais"),
    ]

    SISTEMA_NUMERACAO = "SISTEMA_NUMERACAO"
    MATH_TOPICS = [
        (SISTEMA_NUMERACAO, "Sistema de Numeração"),
    ]

    ALL_TOPICS = PORTUGUESE_TOPICS + MATH_TOPICS
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=ALL_TOPICS, default="")


class Assessment(models.Model):
    PRACTICE_TEST = "simulado"
    EXAM = "prova"

    ASSESSMENT_TYPES = [
        (PRACTICE_TEST, "Simulado"),
        (EXAM, "Prova")
    ]

    title = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=ASSESSMENT_TYPES)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.year})"
    

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    text = models.TextField()
    text_solution = models.TextField()
    video_solution = models.FileField(upload_to='lists_pdfs/', blank=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    

class Passage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='supporting_images/', blank=True, null=True)

    def __str__(self):
        return self.text


class CustomList(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Filter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.text
