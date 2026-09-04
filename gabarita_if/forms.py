from django import forms
from .models import Caderno, Fonte


class CadernoForm(forms.ModelForm):
    # Campos extras para os filtros da interface visual
    instituicao = forms.ModelChoiceField(
        queryset=Fonte.objects.all(),
        required=False,
        empty_label='Instituições: Todas',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    tipo_questao = forms.ChoiceField(
        choices=[('todos', 'Tipos de questão: Todos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    class Meta:
        model = Caderno
        exclude = ['usuario', 'questoes', 'criado_em']
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex.: Caderno de Matemática',
                }
            ),
            'cor': forms.TextInput(
                attrs={
                    'type': 'color',
                    'class': 'form-control form-control-color w-100',
                    'style': 'height: 38px;',
                }
            ),
            'disciplina': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'assunto': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }