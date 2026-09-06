from django.db import migrations


def repair_caderno_schema(apps, schema_editor):
    caderno_model = apps.get_model("gabarita_if", "Caderno")
    table_name = caderno_model._meta.db_table
    connection = schema_editor.connection
    existing_columns = {
        column.name
        for column in connection.introspection.get_table_description(
            connection.cursor(), table_name
        )
    }

    for field in caderno_model._meta.local_fields:
        if field.column not in existing_columns:
            schema_editor.add_field(caderno_model, field)


class Migration(migrations.Migration):
    dependencies = [
        ("gabarita_if", "0006_remove_caderno_ano"),
    ]

    operations = [
        migrations.RunPython(repair_caderno_schema, migrations.RunPython.noop),
    ]