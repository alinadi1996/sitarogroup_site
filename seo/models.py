from django.core.exceptions import ValidationError
from django.db import models


class SchemaMode(models.TextChoices):
    AUTO = "auto", "خودکار"
    CUSTOM = "custom", "اختصاصی"
    DISABLED = "disabled", "غیرفعال"


def validate_schema(value):
    if value in (None, ""):
        return
    nodes = value if isinstance(value, list) else [value]
    if not nodes or not all(isinstance(node, dict) for node in nodes):
        raise ValidationError("اسکیما باید یک شیء JSON یا فهرستی از اشیای JSON باشد.")
    for node in nodes:
        if node.get("@context") not in ("https://schema.org", "http://schema.org"):
            raise ValidationError("هر اسکیما باید @context معتبرِ schema.org داشته باشد.")
        if not node.get("@type") and not node.get("@graph"):
            raise ValidationError("هر اسکیما باید @type یا @graph داشته باشد.")


class SEOFieldsMixin(models.Model):
    seo_title = models.CharField("عنوان اختصاصی سئو", max_length=200, blank=True,
        help_text="اگر خالی باشد، عنوان خود محتوا استفاده می‌شود.")
    meta_description = models.TextField("توضیحات متا", blank=True,
        help_text="اگر خالی باشد، از خلاصه یا ابتدای محتوای صفحه استفاده می‌شود.")
    focus_keyword = models.CharField("عبارت کلیدی هدف", max_length=150, blank=True,
        help_text="فقط برای بررسی داخلی محتواست و به meta keywords تبدیل نمی‌شود.")
    canonical_url = models.URLField("نشانی canonical", blank=True,
        help_text="در صورت خالی بودن، از آدرس اصلی همین صفحه ساخته می‌شود.")
    robots_index = models.BooleanField("اجازه ایندکس", default=True,
        help_text="با غیرفعال‌کردن، دستور noindex تولید می‌شود.")
    robots_follow = models.BooleanField("اجازه دنبال‌کردن پیوندها", default=True,
        help_text="با غیرفعال‌کردن، دستور nofollow تولید می‌شود.")
    og_title = models.CharField("عنوان شبکه‌های اجتماعی", max_length=200, blank=True,
        help_text="اگر خالی باشد، عنوان سئو استفاده می‌شود.")
    og_description = models.TextField("توضیح شبکه‌های اجتماعی", blank=True,
        help_text="اگر خالی باشد، توضیحات متا استفاده می‌شود.")
    og_image = models.ImageField("تصویر شبکه‌های اجتماعی", upload_to="seo/og/%Y/%m/",
        blank=True, help_text="اگر خالی باشد، تصویر شاخص محتوا یا تصویر پیش‌فرض سایت استفاده می‌شود.")
    schema_mode = models.CharField("حالت اسکیما", max_length=12, choices=SchemaMode.choices,
        default=SchemaMode.AUTO, help_text="خودکار، اختصاصی یا غیرفعال.")
    custom_schema = models.JSONField("اسکیمای اختصاصی", blank=True, null=True,
        validators=[validate_schema], help_text="JSON-LD معتبر؛ فقط در حالت اختصاصی رندر می‌شود.")
    seo_updated_at = models.DateTimeField("آخرین ویرایش تنظیمات سئو", auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.schema_mode == SchemaMode.CUSTOM and not self.custom_schema:
            raise ValidationError({"custom_schema": "در حالت اختصاصی، واردکردن اسکیمای معتبر لازم است."})


class StaticPageSEO(SEOFieldsMixin):
    focus_keyword = None
    seo_updated_at = None
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class PageKey(models.TextChoices):
        HOME = "home", "صفحه اصلی"
        CONTACT = "contact", "تماس"
        TOOLS = "tools", "فهرست ابزارها"
        PORTFOLIO_INDEX = "portfolio_index", "فهرست نمونه‌کارها"
        BLOG_INDEX = "blog_index", "فهرست بلاگ"

    page_key = models.CharField("صفحه", max_length=24, choices=PageKey.choices, unique=True)

    class Meta:
        verbose_name = "سئوی صفحه ثابت"
        verbose_name_plural = "سئوی صفحات ثابت"

    def __str__(self):
        return self.get_page_key_display()


class SiteSEOSettings(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    site_name = models.CharField("نام سایت", max_length=160, default="گروه سیتارو")
    default_seo_title = models.CharField("عنوان پیش‌فرض", max_length=200,
        default="گروه سیتارو | طراحی سایت اختصاصی، جنگو، وردپرس و سئو")
    default_meta_description = models.TextField("توضیح پیش‌فرض",
        default="طراحی و توسعه وب‌سایت‌های اختصاصی با Django و WordPress، سئو تکنیکال و بهینه‌سازی سرعت توسط گروه سیتارو.")
    site_url = models.URLField("آدرس اصلی سایت", default="https://sitarogroup.ir/")
    organization_name = models.CharField("نام سازمان", max_length=160, default="گروه سیتارو")
    legal_name = models.CharField("نام حقوقی", max_length=200, blank=True)
    organization_logo = models.ImageField("لوگوی سازمان", upload_to="seo/site/", blank=True)
    organization_description = models.TextField("توضیح سازمان", blank=True)
    contact_email = models.EmailField("ایمیل تماس", blank=True)
    contact_phone = models.CharField("تلفن تماس", max_length=32, blank=True)
    social_links = models.JSONField("پیوندهای شبکه‌های اجتماعی", default=list, blank=True,
        help_text="فهرست JSON از آدرس‌های واقعی شبکه‌های اجتماعی.")
    default_og_image = models.ImageField("تصویر پیش‌فرض شبکه‌های اجتماعی", upload_to="seo/site/", blank=True)
    default_og_type = models.CharField("نوع پیش‌فرض Open Graph", max_length=30, default="website")

    class Meta:
        verbose_name = "تنظیمات سئوی سایت"
        verbose_name_plural = "تنظیمات سئوی سایت"
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="seo_single_site_settings")]

    def __str__(self):
        return "تنظیمات سئوی سایت"

    def clean(self):
        super().clean()
        if not isinstance(self.social_links, list) or any(
            not isinstance(item, str) or not item.startswith("https://") for item in self.social_links
        ):
            raise ValidationError({"social_links": "فهرست باید فقط شامل آدرس‌های HTTPS باشد."})
