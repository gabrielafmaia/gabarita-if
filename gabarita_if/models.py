from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    text = models.TextField()

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

class Assessment(models.Model):
    PRACTICE_TEST = "simulado"
    EXAM = "prova"

    TYPES = [
        (PRACTICE_TEST, "Simulado"),
        (EXAM, "Prova")
    ]

    title = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPES, blank=True, null=True)


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text