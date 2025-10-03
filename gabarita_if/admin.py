from django.contrib import admin
from .models import Question, Subject, Topic, Assessment, Option, Passage

# Registrar todos os modelos necessários
admin.site.register(Question)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Assessment)
admin.site.register(Option)
admin.site.register(Passage)