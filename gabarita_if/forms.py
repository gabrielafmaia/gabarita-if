from django import forms
from .models import Caderno


class CadernoForm(forms.ModelForm):
    class Meta:
        model = Caderno
        fields = "__all__"
        exclude = ["usuario"]
        widgets = {
            "cor": forms.TextInput(attrs={"type": "color", "class": "form-control form-control-color"})
        }