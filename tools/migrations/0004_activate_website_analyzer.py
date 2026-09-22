from django.db import migrations


def activate_website_analyzer(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug="website-analyzer").update(
        title="تحلیل سایت و سرعت",
        short_description="بررسی اطلاعات پایه صفحه و گزارش سرعت موبایل از Google PageSpeed.",
        status="active",
    )


class Migration(migrations.Migration):
    dependencies = [("tools", "0003_activate_image_converter")]

    operations = [migrations.RunPython(activate_website_analyzer, migrations.RunPython.noop)]
