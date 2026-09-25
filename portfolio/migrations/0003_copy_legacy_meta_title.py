from django.db import migrations
from django.db.models import F


def copy_legacy_titles(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    Project.objects.using(schema_editor.connection.alias).filter(seo_title="").exclude(meta_title="").update(
        seo_title=F("meta_title")
    )


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0002_project_canonical_url_project_custom_schema_and_more")]
    operations = [migrations.RunPython(copy_legacy_titles, migrations.RunPython.noop)]
