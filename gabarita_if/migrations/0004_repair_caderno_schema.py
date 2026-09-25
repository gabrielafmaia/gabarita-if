from django.db import migrations


def repair_caderno_schema(apps, schema_editor):
    """Restore Caderno columns omitted from databases with 0001 marked applied."""
    connection = schema_editor.connection
    table_name = "gabarita_if_caderno"

    with connection.cursor() as cursor:
        existing_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor, table_name
            )
        }

    missing_columns = []
    if "status_questao" not in existing_columns:
        missing_columns.append(
            'ADD COLUMN "status_questao" varchar(20) NOT NULL DEFAULT \'todas\''
        )
    if "blocos" not in existing_columns:
        missing_columns.append(
            'ADD COLUMN "blocos" text NOT NULL DEFAULT \'[]\''
        )

    for definition in missing_columns:
        schema_editor.execute(f'ALTER TABLE "{table_name}" {definition}')


class Migration(migrations.Migration):
    dependencies = [
        ("gabarita_if", "0003_alter_questao_ano"),
    ]

    operations = [
        migrations.RunPython(repair_caderno_schema, migrations.RunPython.noop),
    ]
