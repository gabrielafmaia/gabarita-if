from django import forms
from gabarita_if.models import *


class QuestaoForm(forms.ModelForm):
    alternativa_a = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 2}))
    alternativa_b = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 2}))
    alternativa_c = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 2}))
    alternativa_d = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 2}))
    alternativa_correta = forms.ChoiceField(choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])

    class Meta:
        model = Questao
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d", "alternativa_correta"]:
            self.fields[field].label = ""

    def save(self, commit=True):
        questao = super().save(commit=commit)
        
        alternativas = [
            (self.cleaned_data["alternativa_a"], "A"),
            (self.cleaned_data["alternativa_b"], "B"),
            (self.cleaned_data["alternativa_c"], "C"),
            (self.cleaned_data["alternativa_d"], "D"),
        ]
        
        for texto, letra in alternativas:
            Alternativa.objects.create(questao=questao, texto=texto, correta=(self.cleaned_data["alternativa_correta"] == letra))
        
        return questao


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