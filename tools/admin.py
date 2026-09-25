from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Tool, ToolCategory
from seo.admin import SEOAdminMixin, SEO_FIELDS


@admin.register(ToolCategory)
class ToolCategoryAdmin(ModelAdmin):
    list_display = ("title", "slug", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    readonly_fields = ("created_at",)
    list_per_page = 25


@admin.register(Tool)
class ToolAdmin(SEOAdminMixin, ModelAdmin):
    list_display = ("title", "category", "status", "is_featured", "order", "updated_at")
    list_display_links = ("title",)
    list_editable = ("status", "is_featured", "order")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    readonly_fields = ("created_at", "updated_at", "seo_updated_at")
    list_select_related = ("category",)
    list_per_page = 25
    show_full_result_count = False
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "short_description", "icon", "category")}),
        ("نمایش و دسترسی", {"fields": ("status", "is_featured", "order")}),
        ("بهینه‌سازی برای موتورهای جست‌وجو", {"fields": SEO_FIELDS}),
        ("زمان‌بندی", {"fields": ("created_at", "updated_at")}),
    )
