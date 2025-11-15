from django import forms
from gabarita_if.models import *


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"


class ProvaForm(forms.ModelForm):
    class Meta:
        model = Prova
        fields = "__all__"


class SimuladoForm(forms.ModelForm):
    class Meta:
        model = Simulado
        fields = "__all__"


class TextoDeApoioForm(forms.ModelForm):
    class Meta:
        model = TextoDeApoio
        fields = "__all__"