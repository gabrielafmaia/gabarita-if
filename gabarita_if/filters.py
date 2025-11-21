import django_filters
from .models import Questao, Disciplina, Assunto

class QuestaoFiltersSet(django_filters.FilterSet):
    disciplina = django_filters.ModelChoiceFilter(
        queryset=Disciplina.objects.all(),
        empty_label="Todas as disciplinas",
        label="Disciplina"
    )
    
    assunto = django_filters.ModelChoiceFilter(
        queryset=Assunto.objects.all(),
        empty_label="Todos os assuntos",
        label="Assunto"
    )
    
    id = django_filters.NumberFilter(
        label="ID da questão"
    )
    
    class Meta:
        model = Questao
        fields = ["disciplina", "assunto", "id"]