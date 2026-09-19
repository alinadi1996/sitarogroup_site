from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse


class ToolCategory(models.Model):
    title = models.CharField("عنوان", max_length=120)
    slug = models.SlugField("آدرس خوانا", max_length=140, unique=True, allow_unicode=True)
    order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name = "دسته‌بندی ابزار"
        verbose_name_plural = "دسته‌بندی‌های ابزار"

    def __str__(self):
        return self.title


class ToolQuerySet(models.QuerySet):
    def public(self):
        return self.exclude(status=Tool.Status.DISABLED).filter(
            Q(category__isnull=True) | Q(category__is_active=True)
        )


class Tool(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "فعال"
        COMING_SOON = "coming_soon", "به‌زودی"
        DISABLED = "disabled", "غیرفعال"

    title = models.CharField("عنوان", max_length=160)
    slug = models.SlugField("آدرس خوانا", max_length=180, unique=True, allow_unicode=True)
    short_description = models.CharField("توضیح کوتاه", max_length=280)
    icon = models.FileField(
        "آیکون",
        upload_to="tools/icons/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(("svg", "png", "webp"))],
        help_text="اختیاری؛ فرمت SVG، PNG یا WebP.",
    )
    category = models.ForeignKey(
        ToolCategory,
        on_delete=models.SET_NULL,
        related_name="tools",
        verbose_name="دسته‌بندی",
        blank=True,
        null=True,
    )
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.COMING_SOON,
    )
    is_featured = models.BooleanField("ابزار شاخص", default=False)
    order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    objects = ToolQuerySet.as_manager()

    class Meta:
        ordering = ("order", "title")
        verbose_name = "ابزار"
        verbose_name_plural = "ابزارها"

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.status == self.Status.ACTIVE

    def get_absolute_url(self):
        if not self.is_available:
            return ""
        return reverse("tools:launch", kwargs={"slug": self.slug})
