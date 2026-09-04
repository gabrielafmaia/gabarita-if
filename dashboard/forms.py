from django import forms
from gabarita_if.models import *


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"


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

