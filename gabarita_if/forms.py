from django import forms
from django_select2 import forms as s2forms
from .models import ListaPersonalizada


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