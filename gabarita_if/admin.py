from django.contrib import admin
from .models import *

admin.site.register(Disciplina)
admin.site.register(Assunto)
admin.site.register(Prova)
admin.site.register(Simulado)
admin.site.register(Questao)
admin.site.register(TextoDeApoio)
admin.site.register(ListaPersonalizada)
admin.site.register(Comentario)