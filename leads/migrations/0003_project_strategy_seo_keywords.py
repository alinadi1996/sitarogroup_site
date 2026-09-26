import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("leads", "0002_client_project_tracking")]

    operations = [
        migrations.CreateModel(
            name="ProjectStrategy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("summary", models.TextField(verbose_name="خلاصه استراتژی برای مشتری")),
                ("current_focus", models.CharField(max_length=180, verbose_name="تمرکز فعلی")),
                ("next_step", models.TextField(blank=True, verbose_name="گام بعدی")),
                ("is_visible", models.BooleanField(default=True, verbose_name="نمایش به مشتری")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")),
                ("project", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="strategy", to="leads.clientproject", verbose_name="پروژه")),
            ],
            options={"verbose_name": "استراتژی پروژه", "verbose_name_plural": "استراتژی پروژه‌ها"},
        ),
        migrations.CreateModel(
            name="SEOKeyword",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("keyword", models.CharField(max_length=180, verbose_name="کلمه کلیدی")),
                ("target_url", models.URLField(blank=True, verbose_name="صفحه هدف")),
                ("priority", models.CharField(choices=[("primary", "اصلی"), ("secondary", "تکمیلی")], default="secondary", max_length=12, verbose_name="اولویت")),
                ("status", models.CharField(choices=[("research", "در حال تحقیق"), ("planned", "در برنامه محتوا"), ("optimizing", "در حال بهینه‌سازی"), ("tracking", "در حال پایش"), ("achieved", "به هدف رسیده")], default="research", max_length=16, verbose_name="وضعیت")),
                ("current_position", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="جایگاه فعلی")),
                ("is_visible", models.BooleanField(default=True, verbose_name="نمایش به مشتری")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seo_keywords", to="leads.clientproject", verbose_name="پروژه")),
            ],
            options={"ordering": ("order", "keyword"), "verbose_name": "کلمه کلیدی سئو", "verbose_name_plural": "کلمات کلیدی سئو"},
        ),
    ]
