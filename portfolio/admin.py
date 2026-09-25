from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Project, ProjectImage
from seo.admin import SEOAdminMixin, SEO_FIELDS


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "alt_text", "caption", "display_order")


@admin.register(Project)
class ProjectAdmin(SEOAdminMixin, ModelAdmin):
    list_display = ("title", "industry", "is_published", "display_order", "updated_at")
    list_editable = ("is_published", "display_order")
    list_filter = ("is_published", "industry")
    search_fields = ("title", "industry", "summary", "introduction")
    list_per_page = 25
    show_full_result_count = False
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "seo_updated_at", "seo_analysis")
    inlines = (ProjectImageInline,)
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "industry", "summary", "cover", "cover_alt")}),
        ("مطالعه موردی", {"fields": ("introduction", "challenge", "solution", "completed_work", "result", "website_url")}),
        ("بهینه‌سازی برای موتورهای جست‌وجو", {"fields": SEO_FIELDS}),
        ("بررسی داخلی SEO", {"fields": ("seo_analysis",)}),
        ("انتشار", {"fields": ("is_published", "display_order", "created_at", "updated_at")}),
    )
