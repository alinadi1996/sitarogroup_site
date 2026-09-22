from django.db import migrations


def activate_sitemap_robots_generator(apps, schema_editor):
    Tool = apps.get_model("tools", "Tool")
    ToolCategory = apps.get_model("tools", "ToolCategory")
    category = ToolCategory.objects.filter(slug="technical-seo").first()
    Tool.objects.update_or_create(
        slug="sitemap-robots-generator",
        defaults={
            "title": "ساخت Sitemap و Robots.txt",
            "short_description": "فایل‌های sitemap.xml و robots.txt را برای سایت خود آماده کنید.",
            "category": category,
            "status": "active",
            "is_featured": False,
            "order": 35,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("tools", "0005_merge_20260922_2028")]

    operations = [
        migrations.RunPython(activate_sitemap_robots_generator, migrations.RunPython.noop),
    ]
