from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.filters.admin import ChoicesRadioFilter

from .models import ClientProject, ContactRequest, ProjectStrategy, ProjectUpdate, SEOKeyword


@admin.register(ContactRequest)
class ContactRequestAdmin(ModelAdmin):
    list_display = ("full_name", "user", "phone", "service", "status", "created_at")
    list_display_links = ("full_name",)
    list_editable = ("status",)
    list_filter = (("status", ChoicesRadioFilter), "service", "created_at")
    search_fields = ("full_name", "phone", "website_url", "user__username", "user__email")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)
    list_per_page = 25
    show_full_result_count = False
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "اطلاعات درخواست",
            {
                "fields": (
                    "user",
                    "full_name",
                    "phone",
                    "service",
                    "project_description",
                    "website_url",
                    "estimated_budget",
                    "preferred_contact_method",
                )
            },
        ),
        ("پیگیری داخلی", {"fields": ("status", "internal_note")}),
        ("زمان‌بندی", {"fields": ("created_at", "updated_at")}),
    )


class ProjectUpdateInline(StackedInline):
    model = ProjectUpdate
    extra = 0
    fields = ("title", "message", "progress", "is_visible", "created_at")
    readonly_fields = ("created_at",)


class ProjectStrategyInline(StackedInline):
    model = ProjectStrategy
    extra = 0
    max_num = 1
    fields = ("summary", "current_focus", "next_step", "is_visible", "updated_at")
    readonly_fields = ("updated_at",)


class SEOKeywordInline(StackedInline):
    model = SEOKeyword
    extra = 0
    fields = ("keyword", "target_url", "priority", "status", "current_position", "is_visible", "order")
    ordering = ("order", "keyword")


@admin.register(ClientProject)
class ClientProjectAdmin(ModelAdmin):
    list_display = ("title", "client", "service", "status", "progress", "target_date", "updated_at")
    list_editable = ("status", "progress")
    list_filter = (("status", ChoicesRadioFilter), "service", "target_date")
    search_fields = ("title", "client__username", "client__email", "contact_request__full_name")
    autocomplete_fields = ("client", "contact_request")
    list_select_related = ("client",)
    list_per_page = 25
    show_full_result_count = False
    readonly_fields = ("created_at", "updated_at")
    inlines = (ProjectStrategyInline, SEOKeywordInline, ProjectUpdateInline)
    fieldsets = (
        ("پروژه", {"fields": ("client", "contact_request", "title", "service")}),
        ("پیشرفت", {"fields": ("status", "progress", "target_date")}),
        ("زمان‌بندی", {"fields": ("created_at", "updated_at")}),
    )
