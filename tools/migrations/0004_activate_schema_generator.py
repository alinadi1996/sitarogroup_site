from django.db import migrations


def activate_schema_generator(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="schema-generator").update(status="active")


def deactivate_schema_generator(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="schema-generator").update(status="coming_soon")


class Migration(migrations.Migration):
    dependencies = [("tools", "0003_activate_serp_preview")]

    operations = [migrations.RunPython(activate_schema_generator, deactivate_schema_generator)]
