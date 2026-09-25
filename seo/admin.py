from django.contrib import admin
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from .analysis import analyze_content
from .models import SiteSEOSettings, StaticPageSEO


SEO_FIELDS = ("seo_title", "meta_description", "focus_keyword", "canonical_url",
              "robots_index", "robots_follow", "og_title", "og_description",
              "og_image", "schema_mode", "custom_schema", "seo_updated_at")
STATIC_SEO_FIELDS = tuple(field for field in SEO_FIELDS if field not in {"focus_keyword", "seo_updated_at"}) + ("updated_at",)


class SEOAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if field and db_field.name in {"custom_schema", "social_links"}:
            field.error_messages["invalid"] = "ساختار JSON معتبر نیست؛ کلیدها و علامت‌ها را بررسی کنید."
        return field

    @admin.display(description="بررسی داخلی SEO")
    def seo_analysis(self, obj):
        if not obj.pk:
            return "پس از ذخیرهٔ محتوا، چک‌لیست نمایش داده می‌شود."
        rows = format_html_join("", '<li class="seo-check seo-check--{}"><span>{}</span><strong>{}</strong><small>{}</small></li>',
                                (("ok" if item["ok"] else "warn", item["label"],
                                  "تکمیل" if item["ok"] else "نیازمند بررسی", item["detail"])
                                 for item in analyze_content(obj)))
        return format_html('<ul class="seo-checklist">{}</ul>', rows)


@admin.register(StaticPageSEO)
class StaticPageSEOAdmin(SEOAdminMixin, ModelAdmin):
    list_display = ("page_key", "seo_title", "robots_index", "updated_at")
    readonly_fields = ("updated_at",)
    fieldsets = (("صفحه", {"fields": ("page_key",)}),
                 ("بهینه‌سازی برای موتورهای جست‌وجو", {"fields": STATIC_SEO_FIELDS}))

    def get_readonly_fields(self, request, obj=None):
        return (*super().get_readonly_fields(request, obj), *(("page_key",) if obj else ()))

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and "page_key" in form.base_fields:
            used = set(StaticPageSEO.objects.values_list("page_key", flat=True))
            form.base_fields["page_key"].choices = [choice for choice in form.base_fields["page_key"].choices
                                                     if not choice[0] or choice[0] not in used]
        return form


@admin.register(SiteSEOSettings)
class SiteSEOSettingsAdmin(SEOAdminMixin, ModelAdmin):
    fieldsets = (
        ("اطلاعات سایت", {"fields": ("site_name", "site_url", "default_seo_title", "default_meta_description", "default_og_image", "default_og_type")}),
        ("سازمان و داده‌های ساختاریافته", {"fields": ("organization_name", "legal_name", "organization_logo", "organization_description", "contact_email", "contact_phone", "social_links")}),
    )

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteSEOSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
