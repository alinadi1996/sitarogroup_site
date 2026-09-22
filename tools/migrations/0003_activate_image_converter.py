from django.db import migrations


def activate_image_converter(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="image-optimizer").update(
        title="تبدیل تصویر",
        short_description="تبدیل تکی یا گروهی تصاویر به WebP، PNG و JPEG برای استفاده در وب.",
        status="active",
    )


class Migration(migrations.Migration):
    dependencies = [("tools", "0002_seed_initial_tools")]

    operations = [migrations.RunPython(activate_image_converter, migrations.RunPython.noop)]
