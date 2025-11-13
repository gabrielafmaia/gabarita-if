from django import forms
from .models import ListaPersonalizada, Comentario


class ListaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = ListaPersonalizada
        fields = "__all__"
        exclude = ["usuario"]
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = "__all__"
        exclude = ["autor", "criado_em"]