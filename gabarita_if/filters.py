import django_filters as filters
from django import forms
from .models import Assunto, Questao, RespostaQuestao


class AssuntoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        if hasattr(value, "instance"):
            option["attrs"]["data-disciplina-id"] = value.instance.disciplina_id

        return option


class QuestaoFiltro(filters.FilterSet):
    STATUS_OPCOES = [
        ("respondidas", "Respondidas"),
        ("nao_respondidas", "Não Respondidas"),
        ("corretas", "Corretas"),
        ("incorretas", "Incorretas"),
    ]

    status = filters.ChoiceFilter(
        label="Status",
        choices=STATUS_OPCOES,
        method="filtrar_status"
    )

    assunto = filters.ModelChoiceFilter(
        queryset=Assunto.objects.select_related("disciplina").all(),
        method="filtrar_assunto",
        widget=AssuntoSelect,
    )

    ano = filters.NumberFilter(
        label="Ano",
        lookup_expr="exact",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "1900",
            "max": "2100",
            "placeholder": "Ex.: 2024",
        }),
    )

    class Meta:
        model = Questao
        fields = ["disciplina", "assunto", "fonte", "ano", "dificuldade", "codigo"]

    def filtrar_status(self, queryset, name, value):
        usuario = self.request.user
        respostas = RespostaQuestao.objects.filter(
            usuario=usuario,
            tentativa=None
        )

        if value == "respondidas":
            return queryset.filter(respostas__in=respostas)

        if value == "nao_respondidas":
            return queryset.exclude(respostas__in=respostas)

        if value == "corretas":
            return queryset.filter(
                respostas__in=respostas.filter(acertou=True)
            )

        if value == "incorretas":
            return queryset.filter(
                respostas__in=respostas.filter(acertou=False)
            )

        return queryset

    def filtrar_assunto(self, queryset, name, value):
        disciplina = self.form.cleaned_data.get("disciplina")

        if not disciplina or value.disciplina_id != disciplina.id:
            return queryset.none()

        return queryset.filter(assunto=value)
