from django import forms
from django_select2 import forms as s2forms
from gabarita_if.models import *


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = "__all__"
        widgets = {
            "disciplina": s2forms.ModelSelect2Widget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            ),
            "assunto": s2forms.ModelSelect2Widget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            ),
            "prova": s2forms.ModelSelect2Widget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            ),
            "simulados": s2forms.ModelSelect2MultipleWidget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"},
            )
        }


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
        widgets = {
            "prova": s2forms.ModelSelect2Widget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            ),
            "simulados": s2forms.ModelSelect2MultipleWidget(
                search_fields=["titulo__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            ),
            "questoes": s2forms.ModelSelect2MultipleWidget(
                search_fields=["enunciado__icontains"],
                attrs={"data-minimum-input-length": 0, "data-theme": "bootstrap-5", "data-width": "100%"}
            )
        }