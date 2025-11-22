from django import forms
from django_select2 import forms as s2forms
from .models import ListaPersonalizada, Disciplina, Assunto


class ListaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = ListaPersonalizada
        fields = "__all__"
        exclude = ["usuario"]
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
            "questoes": s2forms.ModelSelect2MultipleWidget(
                search_fields=["enunciado__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            )
        }


class FiltroForm(forms.Form):
    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label="Todas as disciplinas"
    )
    
    assunto = forms.ModelChoiceField(
        queryset=Assunto.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label="Todos os assuntos"
    )
    
    id_questao = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite o código da questão"}),
        label="Código da questão"
    )