import django_filters as filters
from .models import Questao, RespostaUsuario


class QuestaoFiltro(filters.FilterSet):
    STATUS_OPCOES = [
        ("respondidas", "Respondidas"),
        ("nao_respondidas", "Não Respondidas"),
        ("corretas", "Corretas"),
        ("incorretas", "Incorretas"),
    ]

    status = filters.ChoiceFilter(
        label="Status das Questões",
        choices=STATUS_OPCOES,
        method="filtrar_status"
    )

    class Meta:
        model = Questao
        fields = ["disciplina", "assunto", "id"]

    def filtrar_status(self, queryset, name, value):
        usuario = self.request.user
        respostas = RespostaUsuario.objects.filter(usuario=usuario, simulado=None, prova=None)

        if value == "respondidas":
            return queryset.filter(respostas__in=respostas)

        if value == "nao_respondidas":
            return queryset.exclude(respostas__in=respostas)

        if value == "corretas":
            return queryset.filter(respostas__in=respostas.filter(acertou=True))

        if value == "incorretas":
            return queryset.filter(respostas__in=respostas.filter(acertou=False))

        return queryset
