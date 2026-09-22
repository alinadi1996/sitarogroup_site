import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("leads", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactrequest",
            name="user",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="contact_requests", to=settings.AUTH_USER_MODEL, verbose_name="حساب کاربری"),
        ),
        migrations.CreateModel(
            name="ClientProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, verbose_name="نام پروژه")),
                ("service", models.CharField(choices=[("web_design", "طراحی سایت"), ("custom_development", "توسعه اختصاصی"), ("seo_performance", "سئو و بهینه‌سازی عملکرد"), ("automation", "اتوماسیون"), ("consultation", "مشاوره"), ("other", "سایر")], max_length=32, verbose_name="خدمت")),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("discovery", "کشف و برنامه‌ریزی"), ("design", "طراحی"), ("development", "توسعه"), ("review", "بازبینی و تأیید"), ("launch", "آماده انتشار"), ("completed", "تکمیل‌شده")], default="pending", max_length=16, verbose_name="مرحله فعلی")),
                ("progress", models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name="درصد پیشرفت")),
                ("target_date", models.DateField(blank=True, null=True, verbose_name="تاریخ هدف")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")),
                ("client", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="client_projects", to=settings.AUTH_USER_MODEL, verbose_name="مشتری")),
                ("contact_request", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="client_project", to="leads.contactrequest", verbose_name="درخواست اولیه")),
            ],
            options={"verbose_name": "پروژه مشتری", "verbose_name_plural": "پروژه‌های مشتریان", "ordering": ("-updated_at",)},
        ),
        migrations.CreateModel(
            name="ProjectUpdate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, verbose_name="عنوان به‌روزرسانی")),
                ("message", models.TextField(verbose_name="شرح برای مشتری")),
                ("progress", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name="درصد پیشرفت در این به‌روزرسانی")),
                ("is_visible", models.BooleanField(default=True, verbose_name="نمایش به مشتری")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="updates", to="leads.clientproject", verbose_name="پروژه")),
            ],
            options={"verbose_name": "به‌روزرسانی پروژه", "verbose_name_plural": "به‌روزرسانی‌های پروژه", "ordering": ("-created_at",)},
        ),
    ]
