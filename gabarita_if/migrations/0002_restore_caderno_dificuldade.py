from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gabarita_if", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.AddField(
                    model_name="caderno",
                    name="dificuldade",
                    field=models.JSONField(blank=True, default=list),
                ),
            ],
        ),
    ]
