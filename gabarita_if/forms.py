from django import forms
from .models import ListaPersonalizada, Comentario, Questao, Disciplina, Assunto, Prova


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


class FiltroForm(forms.Form):
    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label="Todas as disciplinas"
    )
    
    assunto = forms.ModelChoiceField(
        queryset=Assunto.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label="Todos os assuntos"
    )
    
    ano = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select,
        label="Ano"
    )
    
    id_questao = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite o código da questão"}),
        label="Código da questão"
    )
    
    TIPO_AVALIACAO = [
        ("", "Todos os tipos"),
        ("prova", "Somente questões de provas"),
        ("simulado", "Somente questões de simulados"),
    ]
    
    tipo_avaliacao = forms.ChoiceField(
        choices=TIPO_AVALIACAO,
        required=False,
        widget=forms.RadioSelect,
        label="Tipo de questão"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        anos_provas = Prova.objects.values_list("ano", flat=True).distinct().order_by("-ano")
        anos_choices = [("", "Todos os anos")] + [(ano, ano) for ano in anos_provas]
        self.fields["ano"].choices = anos_choices