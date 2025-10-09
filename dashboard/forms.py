from django import forms
from gabarita_if.models import Questao
from usuarios.models import Usuario

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"