from django import forms
from gabarita_if.models import Questao, Alternativa, Avaliacao, TextoDeApoio

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"

class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = "__all__"

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = "__all__"


class TextoDeApoioForm(forms.ModelForm):
    class Meta:
        model = TextoDeApoio
        fields = "__all__"