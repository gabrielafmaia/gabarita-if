from django import forms
from .models import ListaPersonalizada, Filtro, Comentario


class ListaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = ListaPersonalizada
        fields = "__all__"
        exclude = ["usuario"]
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }


class FiltroForm(forms.ModelForm):
    class Meta:
        model = Filtro
        fields = "__all__"
        exclude = ["usuario", "criado_em"]


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = "__all__"
        exclude = ["autor", "criado_em"]