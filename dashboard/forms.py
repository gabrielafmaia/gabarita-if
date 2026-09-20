from django import forms
from gabarita_if.models import *
from gabarita_if.filters import AssuntoSelect


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"
        widgets = {
            "assunto": AssuntoSelect,
        }

    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get("disciplina")
        assunto = cleaned_data.get("assunto")

        if disciplina and assunto and assunto.disciplina_id != disciplina.id:
            self.add_error(
                "assunto",
                "Selecione um assunto pertencente à disciplina escolhida.",
            )

        return cleaned_data


class AvaliacaoForm(forms.ModelForm):
    # Sobrescrita do campo ano para aceitar entrada de texto/número com limites de ano
    ano = forms.IntegerField(
        label="Ano",
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ex: 2026',
            'class': 'form-control',
            'min': '1900',
            'max': '2100'
        })
    )

    class Meta:
        model = Avaliacao
        fields = "__all__"


class TextoApoioForm(forms.ModelForm):
    class Meta:
        model = TextoApoio
        fields = "__all__"

