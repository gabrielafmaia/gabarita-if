from django.db import migrations, models


def converter_dificuldade_para_lista(apps, schema_editor):
    Caderno = apps.get_model("gabarita_if", "Caderno")

    for caderno in Caderno.objects.all().iterator():
        valor = caderno.dificuldade
        caderno.dificuldade_lista = [valor] if valor else []
        caderno.save(update_fields=["dificuldade_lista"])


class Migration(migrations.Migration):

    dependencies = [
        ("gabarita_if", "0010_caderno_dificuldade"),
    ]

    operations = [
        migrations.AddField(
            model_name="caderno",
            name="dificuldade_lista",
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.RunPython(converter_dificuldade_para_lista, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="caderno",
            name="dificuldade",
        ),
        migrations.RenameField(
            model_name="caderno",
            old_name="dificuldade_lista",
            new_name="dificuldade",
        ),
    ]