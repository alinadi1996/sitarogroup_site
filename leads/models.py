from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="contact_requests", verbose_name="حساب کاربری", blank=True, null=True)
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


class ClientProject(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        DISCOVERY = "discovery", "کشف و برنامه‌ریزی"
        DESIGN = "design", "طراحی"
        DEVELOPMENT = "development", "توسعه"
        REVIEW = "review", "بازبینی و تأیید"
        LAUNCH = "launch", "آماده انتشار"
        COMPLETED = "completed", "تکمیل‌شده"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_projects", verbose_name="مشتری")
    contact_request = models.OneToOneField(ContactRequest, on_delete=models.SET_NULL, related_name="client_project", verbose_name="درخواست اولیه", blank=True, null=True)
    title = models.CharField("نام پروژه", max_length=180)
    service = models.CharField("خدمت", max_length=32, choices=ContactRequest.Service.choices)
    status = models.CharField("مرحله فعلی", max_length=16, choices=Status.choices, default=Status.PENDING)
    progress = models.PositiveSmallIntegerField("درصد پیشرفت", default=5, validators=[MinValueValidator(0), MaxValueValidator(100)])
    target_date = models.DateField("تاریخ هدف", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "پروژه مشتری"
        verbose_name_plural = "پروژه‌های مشتریان"

    def __str__(self):
        return f"{self.title} — {self.client}"


class ProjectUpdate(models.Model):
    project = models.ForeignKey(ClientProject, on_delete=models.CASCADE, related_name="updates", verbose_name="پروژه")
    title = models.CharField("عنوان به‌روزرسانی", max_length=180)
    message = models.TextField("شرح برای مشتری")
    progress = models.PositiveSmallIntegerField("درصد پیشرفت در این به‌روزرسانی", validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_visible = models.BooleanField("نمایش به مشتری", default=True)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "به‌روزرسانی پروژه"
        verbose_name_plural = "به‌روزرسانی‌های پروژه"

    def __str__(self):
        return f"{self.project} — {self.title}"


class ProjectStrategy(models.Model):
    project = models.OneToOneField(
        ClientProject,
        on_delete=models.CASCADE,
        related_name="strategy",
        verbose_name="پروژه",
    )
    summary = models.TextField("خلاصه استراتژی برای مشتری")
    current_focus = models.CharField("تمرکز فعلی", max_length=180)
    next_step = models.TextField("گام بعدی", blank=True)
    is_visible = models.BooleanField("نمایش به مشتری", default=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "استراتژی پروژه"
        verbose_name_plural = "استراتژی پروژه‌ها"

    def __str__(self):
        return f"استراتژی {self.project}"


class SEOKeyword(models.Model):
    class Priority(models.TextChoices):
        PRIMARY = "primary", "اصلی"
        SECONDARY = "secondary", "تکمیلی"

    class Status(models.TextChoices):
        RESEARCH = "research", "در حال تحقیق"
        PLANNED = "planned", "در برنامه محتوا"
        OPTIMIZING = "optimizing", "در حال بهینه‌سازی"
        TRACKING = "tracking", "در حال پایش"
        ACHIEVED = "achieved", "به هدف رسیده"

    project = models.ForeignKey(
        ClientProject,
        on_delete=models.CASCADE,
        related_name="seo_keywords",
        verbose_name="پروژه",
    )
    keyword = models.CharField("کلمه کلیدی", max_length=180)
    target_url = models.URLField("صفحه هدف", blank=True)
    priority = models.CharField("اولویت", max_length=12, choices=Priority.choices, default=Priority.SECONDARY)
    status = models.CharField("وضعیت", max_length=16, choices=Status.choices, default=Status.RESEARCH)
    current_position = models.PositiveSmallIntegerField("جایگاه فعلی", blank=True, null=True)
    is_visible = models.BooleanField("نمایش به مشتری", default=True)
    order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ("order", "keyword")
        verbose_name = "کلمه کلیدی سئو"
        verbose_name_plural = "کلمات کلیدی سئو"

    def __str__(self):
        return f"{self.keyword} — {self.project}"
