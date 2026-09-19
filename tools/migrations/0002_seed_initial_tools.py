from django.db import migrations


CATEGORIES = (
    ("بررسی سایت", "site-audit", 10),
    ("سئو", "seo", 20),
    ("سئو فنی", "technical-seo", 30),
    ("محتوا", "content", 40),
    ("پرفورمنس", "performance", 50),
    ("کسب‌وکار", "business", 60),
)

TOOLS = (
    {
        "title": "تحلیل سایت",
        "slug": "website-analyzer",
        "category_slug": "site-audit",
        "short_description": "برای شروع یک بررسی منظم از ساختار، سئو و وضعیت فنی وب‌سایت.",
        "is_featured": True,
        "order": 10,
    },
    {
        "title": "پیش‌نمایش نتیجه گوگل",
        "slug": "serp-preview",
        "category_slug": "seo",
        "short_description": "برای مشاهده چیدمان عنوان، آدرس و توضیحات صفحه پیش از انتشار.",
        "is_featured": False,
        "order": 20,
    },
    {
        "title": "بررسی Robots و Sitemap",
        "slug": "robots-sitemap-checker",
        "category_slug": "technical-seo",
        "short_description": "برای مرور فایل‌های راهنمای خزنده‌ها و مسیرهای معرفی‌شده به موتور جست‌وجو.",
        "is_featured": False,
        "order": 30,
    },
    {
        "title": "ساخت Schema",
        "slug": "schema-generator",
        "category_slug": "technical-seo",
        "short_description": "برای آماده‌سازی ساختار اولیه داده‌های ساختاریافته متناسب با نوع محتوا.",
        "is_featured": False,
        "order": 40,
    },
    {
        "title": "تحلیل محتوای فارسی",
        "slug": "persian-content-analyzer",
        "category_slug": "content",
        "short_description": "برای مرور خوانایی و ساختار محتوای فارسی پیش از انتشار یا بازنویسی.",
        "is_featured": False,
        "order": 50,
    },
    {
        "title": "بهینه‌سازی تصویر",
        "slug": "image-optimizer",
        "category_slug": "performance",
        "short_description": "برای آماده‌سازی تصاویر سبک‌تر و مناسب‌تر برای استفاده در صفحات وب.",
        "is_featured": False,
        "order": 60,
    },
    {
        "title": "برنامه‌ریز پروژه",
        "slug": "project-planner",
        "category_slug": "business",
        "short_description": "برای مرتب‌کردن نیازها، اولویت‌ها و گام‌های اولیه یک پروژه دیجیتال.",
        "is_featured": False,
        "order": 70,
    },
)


def seed_tools(apps, schema_editor):
    ToolCategory = apps.get_model("tools", "ToolCategory")
    Tool = apps.get_model("tools", "Tool")

    categories = {}
    for title, slug, order in CATEGORIES:
        category, _ = ToolCategory.objects.update_or_create(
            slug=slug,
            defaults={"title": title, "order": order, "is_active": True},
        )
        categories[slug] = category

    for item in TOOLS:
        data = item.copy()
        category_slug = data.pop("category_slug")
        Tool.objects.update_or_create(
            slug=data.pop("slug"),
            defaults={
                **data,
                "category": categories[category_slug],
                "status": "coming_soon",
            },
        )


def remove_seeded_tools(apps, schema_editor):
    ToolCategory = apps.get_model("tools", "ToolCategory")
    Tool = apps.get_model("tools", "Tool")
    Tool.objects.filter(slug__in=[item["slug"] for item in TOOLS]).delete()
    ToolCategory.objects.filter(slug__in=[item[1] for item in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("tools", "0001_initial")]

    operations = [migrations.RunPython(seed_tools, remove_seeded_tools)]
