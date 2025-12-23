from django.contrib import admin
from .models import *

admin.site.register(Disciplina)
admin.site.register(Assunto)
admin.site.register(Fonte)
admin.site.register(Questao)
admin.site.register(Comentario)
admin.site.register(Avaliacao)
admin.site.register(TextoApoio)
admin.site.register(Caderno)
admin.site.register(RespostaAvaliacao)
admin.site.register(RespostaQuestao)