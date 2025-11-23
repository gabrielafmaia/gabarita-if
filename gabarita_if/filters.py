import django_filters as filters
from .models import Questao

class QuestaoFiltro(filters.FilterSet):
    class Meta:
        model = Questao
        fields = ["disciplina", "assunto", "prova", "simulados", "id"]