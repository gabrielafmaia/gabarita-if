from django.db import migrations, models
from django.db.models import Q
from django.utils import timezone


def manter_uma_tentativa_ativa(apps, schema_editor):
    RespostaAvaliacao = apps.get_model("gabarita_if", "RespostaAvaliacao")
    banco = schema_editor.connection.alias
    tentativas_ativas = (
        RespostaAvaliacao.objects.using(banco)
        .filter(finalizada=False, avaliacao__isnull=False)
        .order_by("pk")
        .values_list("pk", "usuario_id", "avaliacao_id")
    )
    pares_encontrados = set()
    agora = timezone.now()

    for tentativa_id, usuario_id, avaliacao_id in tentativas_ativas.iterator():
        par = (usuario_id, avaliacao_id)
        if par in pares_encontrados:
            RespostaAvaliacao.objects.using(banco).filter(pk=tentativa_id).update(
                finalizada=True,
                finalizada_em=agora,
                tempo_gasto_segundos=0,
            )
        else:
            pares_encontrados.add(par)


class Migration(migrations.Migration):

    dependencies = [
        ("gabarita_if", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="respostaavaliacao",
            name="iniciada_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="respostaavaliacao",
            name="finalizada_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="respostaavaliacao",
            name="tempo_gasto_segundos",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            manter_uma_tentativa_ativa,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="respostaavaliacao",
            constraint=models.UniqueConstraint(
                fields=("usuario", "avaliacao"),
                condition=Q(finalizada=False, avaliacao__isnull=False),
                name="unique_active_assessment_attempt",
            ),
        ),
    ]
