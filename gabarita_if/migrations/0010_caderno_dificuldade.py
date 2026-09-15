from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gabarita_if", "0009_remove_caderno_ano_alter_caderno_cor"),
    ]

    operations = [
        migrations.AddField(
            model_name="caderno",
            name="dificuldade",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Fácil", "Fácil"),
                    ("Média", "Média"),
                    ("Difícil", "Difícil"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]