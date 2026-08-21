from django import forms
from .models import Caderno


class CadernoForm(forms.ModelForm):

    quantidade = forms.IntegerField(
        label="Quantidade de questões",
        initial=10,
        min_value=1,
        max_value=100,
    )

    dificuldades = forms.MultipleChoiceField(
        label="Dificuldade",
        required=False,
        choices=[
            ("Fácil", "Fácil"),
            ("Média", "Média"),
            ("Difícil", "Difícil"),
        ],
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Caderno

        fields = [
            "nome",
            "disciplina",
            "assunto",
            "ano",
            "cor",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Caderno de Matemática",
                }
            ),

            "ano": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: 2025",
                }
            ),

            "cor": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["assunto"].required = False