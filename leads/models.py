from django.db import models


class ContactRequest(models.Model):
    class Service(models.TextChoices):
        WEB_DESIGN = "web_design", "طراحی سایت"
        CUSTOM_DEVELOPMENT = "custom_development", "توسعه اختصاصی"
        SEO_PERFORMANCE = "seo_performance", "سئو و بهینه‌سازی عملکرد"
        AUTOMATION = "automation", "اتوماسیون"
        CONSULTATION = "consultation", "مشاوره"
        OTHER = "other", "سایر"

    class ContactMethod(models.TextChoices):
        PHONE = "phone", "تماس تلفنی"
        WHATSAPP = "whatsapp", "واتساپ"
        TELEGRAM = "telegram", "تلگرام"

    class Status(models.TextChoices):
        NEW = "new", "جدید"
        REVIEWED = "reviewed", "بررسی‌شده"
        CONTACTED = "contacted", "تماس گرفته‌شده"
        CONVERTED = "converted", "تبدیل‌شده"
        REJECTED = "rejected", "ردشده"

    full_name = models.CharField("نام و نام خانوادگی", max_length=150)
    phone = models.CharField("شماره موبایل", max_length=13)
    service = models.CharField("نوع خدمت", max_length=32, choices=Service.choices)
    project_description = models.TextField("توضیحات پروژه")
    website_url = models.URLField("آدرس وب‌سایت", blank=True)
    estimated_budget = models.CharField("بودجه تقریبی", max_length=150, blank=True)
    preferred_contact_method = models.CharField(
        "روش ارتباط ترجیحی",
        max_length=16,
        choices=ContactMethod.choices,
        default=ContactMethod.PHONE,
    )
    status = models.CharField(
        "وضعیت",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    internal_note = models.TextField("یادداشت داخلی", blank=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "درخواست همکاری"
        verbose_name_plural = "درخواست‌های همکاری"

    def __str__(self):
        return f"{self.full_name} — {self.phone}"

