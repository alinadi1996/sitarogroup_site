from django.db import migrations


def activate_serp_preview(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="serp-preview").update(status="active")


def deactivate_serp_preview(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="serp-preview").update(status="coming_soon")


class Migration(migrations.Migration):
    dependencies = [("tools", "0002_seed_initial_tools")]

    operations = [migrations.RunPython(activate_serp_preview, deactivate_serp_preview)]
