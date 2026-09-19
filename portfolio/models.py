from django.db import models
from django.urls import reverse


class ProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Project(models.Model):
    title = models.CharField("نام پروژه", max_length=180)
    slug = models.SlugField("آدرس خوانا", max_length=200, unique=True, allow_unicode=True)
    industry = models.CharField("حوزه فعالیت", max_length=120)
    summary = models.CharField("خلاصه یک‌خطی", max_length=240)
    cover = models.ImageField("تصویر اصلی", upload_to="portfolio/covers/%Y/%m/")
    cover_alt = models.CharField("متن جایگزین تصویر اصلی", max_length=200)
    introduction = models.TextField("معرفی")
    challenge = models.TextField("مسئله")
    solution = models.TextField("راه‌حل")
    completed_work = models.TextField(
        "کارهای انجام‌شده",
        help_text="هر مورد را در یک خط جداگانه وارد کنید.",
    )
    result = models.TextField("نتیجه", blank=True)
    website_url = models.URLField("لینک سایت", blank=True)
    meta_title = models.CharField(
        "عنوان سئو",
        max_length=70,
        blank=True,
        help_text="اختیاری؛ در صورت خالی بودن، نام پروژه استفاده می‌شود.",
    )
    meta_description = models.CharField(
        "توضیحات متا",
        max_length=160,
        blank=True,
        help_text="اختیاری؛ در صورت خالی بودن، خلاصه یک‌خطی استفاده می‌شود.",
    )
    is_published = models.BooleanField("منتشر شده", default=False)
    display_order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ("display_order", "-created_at")
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("portfolio:project_detail", kwargs={"slug": self.slug})

    @property
    def completed_work_items(self):
        return [item.strip() for item in self.completed_work.splitlines() if item.strip()]


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="پروژه",
    )
    image = models.ImageField("تصویر", upload_to="portfolio/gallery/%Y/%m/")
    alt_text = models.CharField("متن جایگزین تصویر", max_length=200)
    caption = models.CharField("توضیح تصویر", max_length=240, blank=True)
    display_order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ("display_order", "id")
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری"

    def __str__(self):
        return f"{self.project} — {self.alt_text}"
