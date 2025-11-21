import django_tables2 as tables
from django.template.defaultfilters import truncatechars
from gabarita_if.models import Questao, Prova, Simulado, TextoDeApoio
from usuarios.models import Usuario


class TabelaBase(tables.Table):
    acoes = tables.TemplateColumn(
        template_name="dashboard/partials/_acoes.html", 
        verbose_name="Ações", 
        orderable=False
    )
    
    class Meta:
        attrs = {"class": "table table-hover table-striped m-0"}


class QuestaoTabela(TabelaBase):
    class Meta(TabelaBase.Meta):
        model = Questao
        fields = ["id", "disciplina", "assunto", "prova", "simulados", "enunciado", "alternativa_correta"]


class ProvaTabela(TabelaBase):
    class Meta(TabelaBase.Meta):
        model = Prova
        fields = ["id", "ano", "titulo", "instituicao"]


class SimuladoTabela(TabelaBase):
    class Meta(TabelaBase.Meta):
        model = Simulado
        fields = ["id", "ano", "titulo", "subtitulo"]


class TextoDeApoioTabela(TabelaBase):
    class Meta(TabelaBase.Meta):
        model = TextoDeApoio
        fields = ["id", "prova", "simulados", "questoes", "titulo", "texto", "imagem"]


class UsuarioTabela(TabelaBase):
    class Meta(TabelaBase.Meta):
        model = Usuario
        fields = ["id", "username", "first_name", "last_name", "email"]