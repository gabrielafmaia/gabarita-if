from django import forms
from .models import ListaPersonalizada


class ListaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = ListaPersonalizada
        fields = "__all__"
        exclude = ["usuario"]
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"})
        }