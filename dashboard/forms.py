from django import forms
from gabarita_if.models import *


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = "__all__"


class TextoApoioForm(forms.ModelForm):
    class Meta:
        model = TextoApoio
        fields = "__all__"