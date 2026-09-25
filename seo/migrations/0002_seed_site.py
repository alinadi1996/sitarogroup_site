from django.db import migrations


def seed_site_settings(apps, schema_editor):
    Settings = apps.get_model("seo", "SiteSEOSettings")
    Settings.objects.using(schema_editor.connection.alias).get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [("seo", "0001_initial")]
    operations = [migrations.RunPython(seed_site_settings, migrations.RunPython.noop)]
