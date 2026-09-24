import django_tables2 as tables
from gabarita_if.models import Questao, Avaliacao, TextoApoio
from usuarios.models import Usuario
from django.utils.html import strip_tags


class TabelaBase(tables.Table):
    acoes = tables.TemplateColumn(
        template_name="dashboard/partials/_acoes.html",
        verbose_name="Ações",
        orderable=False
    )


class QuestaoTabela(TabelaBase):

    def render_enunciado(self, value):
        return strip_tags(value)[:50] + "..."

    class Meta:
        model = Questao
        fields = [
            "id",
            "disciplina",
            "assunto",
            "enunciado",
            "alternativa_correta"
        ]


class AvaliacaoTabela(TabelaBase):

    class Meta:
        model = Avaliacao
        fields = [
            "id",
            "titulo",
            "subtitulo",
            "ano",
            "fonte",
            "questoes"
        ]


class TextoApoioTabela(TabelaBase):

    def render_texto(self, value):
        return strip_tags(value or "")[:50]

    class Meta:
        model = TextoApoio
        fields = [
            "id",
            "titulo",
            "texto",
            "imagem",
            "questoes"
        ]


class UsuarioTabela(TabelaBase):

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email"
        ]
