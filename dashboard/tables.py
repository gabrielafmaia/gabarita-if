import django_tables2 as tables
from gabarita_if.models import Questao, Prova, Simulado, TextoDeApoio
from usuarios.models import Usuario


class QuestaoTabela(tables.Table):
    acoes = tables.TemplateColumn(template_name="dashboard/partials/_acoes.html", verbose_name="Ações", orderable=False)

    class Meta:
        model = Questao
        exclude = ()
        attrs = {"class": "table table-hover table-striped m-0"}


class ProvaTabela(tables.Table):
    acoes = tables.TemplateColumn(template_name="dashboard/partials/_acoes.html", verbose_name="Ações", orderable=False)

    class Meta:
        model = Prova
        exclude = ()
        attrs = {"class": "table table-hover table-striped m-0"}


class SimuladoTabela(tables.Table):
    acoes = tables.TemplateColumn(template_name="dashboard/partials/_acoes.html", verbose_name="Ações", orderable=False)

    class Meta:
        model = Simulado
        exclude = ()
        attrs = {"class": "table table-hover table-striped m-0"}


class TextoDeApoioTabela(tables.Table):
    acoes = tables.TemplateColumn(template_name="dashboard/partials/_acoes.html", verbose_name="Ações", orderable=False)

    class Meta:
        model = TextoDeApoio
        exclude = ()
        attrs = {"class": "table table-hover table-striped m-0"}


class UsuarioTabela(tables.Table):
    acoes = tables.TemplateColumn(template_name="dashboard/partials/_acoes.html", verbose_name="Ações", orderable=False)

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "curso"]
        attrs = {"class": "table table-hover table-striped m-0"}