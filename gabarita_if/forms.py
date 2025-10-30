from django import forms
from .models import ListaPersonalizada, Filtro

class ListaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = ListaPersonalizada
        fields = "__all__"
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }

class FiltroForm(forms.ModelForm):
    class Meta:
        model = Filtro
        fields = "__all__"
        exclude = ["criado_em"]