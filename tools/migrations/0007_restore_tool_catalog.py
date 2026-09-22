from django.db import migrations


CATEGORIES = (
    ("بررسی سایت", "site-audit", 10), ("سئو", "seo", 20),
    ("سئو فنی", "technical-seo", 30), ("محتوا", "content", 40),
    ("پرفورمنس", "performance", 50), ("کسب‌وکار", "business", 60),
)

TOOLS = (
    ("تحلیل سایت و سرعت", "website-analyzer", "site-audit", "بررسی اطلاعات پایه صفحه و گزارش سرعت موبایل از Google PageSpeed.", "active", True, 10),
    ("پیش‌نمایش نتیجه گوگل", "serp-preview", "seo", "چیدمان عنوان، آدرس و توضیحات صفحه را پیش از انتشار بررسی کنید.", "active", False, 20),
    ("بررسی Robots و Sitemap", "robots-sitemap-checker", "technical-seo", "فایل‌های راهنمای خزنده‌ها و مسیرهای معرفی‌شده به موتور جست‌وجو را مرور کنید.", "coming_soon", False, 30),
    ("ساخت Sitemap و Robots.txt", "sitemap-robots-generator", "technical-seo", "فایل‌های sitemap.xml و robots.txt را برای سایت خود آماده کنید.", "active", False, 35),
    ("ساخت Schema", "schema-generator", "technical-seo", "ساختار اولیه داده‌های ساختاریافته متناسب با نوع محتوا را آماده کنید.", "active", False, 40),
    ("تحلیل محتوای فارسی", "persian-content-analyzer", "content", "خوانایی و ساختار محتوای فارسی را پیش از انتشار یا بازنویسی مرور کنید.", "coming_soon", False, 50),
    ("تبدیل تصویر", "image-optimizer", "performance", "تبدیل تکی یا گروهی تصاویر به WebP، PNG و JPEG برای استفاده در وب.", "active", False, 60),
    ("برنامه‌ریز پروژه", "project-planner", "business", "نیازها، اولویت‌ها و گام‌های اولیه یک پروژه دیجیتال را مرتب کنید.", "coming_soon", False, 70),
)


def restore_tool_catalog(apps, schema_editor):
    ToolCategory = apps.get_model("tools", "ToolCategory")
    Tool = apps.get_model("tools", "Tool")
    categories = {}
    for title, slug, order in CATEGORIES:
        category, _ = ToolCategory.objects.update_or_create(slug=slug, defaults={"title": title, "order": order, "is_active": True})
        categories[slug] = category
    for title, slug, category_slug, description, status, featured, order in TOOLS:
        Tool.objects.update_or_create(slug=slug, defaults={"title": title, "short_description": description, "category": categories[category_slug], "status": status, "is_featured": featured, "order": order})


class Migration(migrations.Migration):
    dependencies = [("tools", "0006_activate_sitemap_robots_generator")]
    operations = [migrations.RunPython(restore_tool_catalog, migrations.RunPython.noop)]
