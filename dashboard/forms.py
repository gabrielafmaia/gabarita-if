from django import forms
from django.utils.html import strip_tags
from gabarita_if.models import *
from gabarita_if.filters import AssuntoSelect


class QuestaoForm(forms.ModelForm):
    CAMPOS_ALTERNATIVAS = (
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
    )

    class Meta:
        model = Questao
        fields = "__all__"
        widgets = {
            "assunto": AssuntoSelect,
            "ano": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1900",
                "max": "2100",
                "placeholder": "Ex.: 2024",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for nome in self.CAMPOS_ALTERNATIVAS:
                self.initial[nome] = strip_tags(getattr(self.instance, nome) or "")

    def _clean_alternativa(self, nome):
        valor = self.cleaned_data[nome]
        original = getattr(self.instance, nome, "") or ""
        if self.instance.pk and valor == strip_tags(original):
            return original
        return valor

    def clean_alternativa_a(self):
        return self._clean_alternativa("alternativa_a")

    def clean_alternativa_b(self):
        return self._clean_alternativa("alternativa_b")

    def clean_alternativa_c(self):
        return self._clean_alternativa("alternativa_c")

    def clean_alternativa_d(self):
        return self._clean_alternativa("alternativa_d")

    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get("disciplina")
        assunto = cleaned_data.get("assunto")

        if disciplina and assunto and assunto.disciplina_id != disciplina.id:
            self.add_error(
                "assunto",
                "Selecione um assunto pertencente à disciplina escolhida.",
            )

        return cleaned_data


class AvaliacaoForm(forms.ModelForm):
    # Sobrescrita do campo ano para aceitar entrada de texto/número com limites de ano
    ano = forms.IntegerField(
        label="Ano",
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ex: 2026',
            'class': 'form-control',
            'min': '1900',
            'max': '2100'
        })
    )

    class Meta:
        model = Avaliacao
        exclude = ("questoes", "blocos")

    def clean(self):
        cleaned_data = super().clean()
        from gabarita_if.models import Assunto
        import re
        indices = sorted({
            int(match.group(1)) for key in self.data
            if (match := re.match(r"blocos\[(\d+)\]\[disciplina\]$", key))
        })
        if (
            indices
            and self.instance
            and self.instance.pk
            and not self.instance.blocos
            and all(
                not self.data.get(f"blocos[{index}][disciplina]")
                and not self.data.get(f"blocos[{index}][assunto]")
                for index in indices
            )
        ):
            return cleaned_data
        if not indices and not (self.instance and self.instance.pk):
            raise forms.ValidationError("Adicione ao menos um bloco de questões.")
        for index in indices:
            disciplina = self.data.get(f"blocos[{index}][disciplina]")
            assunto = self.data.get(f"blocos[{index}][assunto]")
            if not disciplina:
                raise forms.ValidationError(f"Informe uma disciplina no bloco {index + 1}.")
            if assunto and not Assunto.objects.filter(pk=assunto, disciplina_id=disciplina).exists():
                raise forms.ValidationError(f"O assunto do bloco {index + 1} não pertence à disciplina selecionada.")
            ano = self.data.get(f"blocos[{index}][ano]", "")
            if ano and (not ano.isdigit() or not 1900 <= int(ano) <= 2100):
                raise forms.ValidationError(f"Informe um ano válido no bloco {index + 1}.")
        return cleaned_data


class TextoApoioForm(forms.ModelForm):
    class Meta:
        model = TextoApoio
        fields = "__all__"

