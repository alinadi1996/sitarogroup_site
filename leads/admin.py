from django.contrib import admin

from .models import ClientProject, ContactRequest, ProjectUpdate


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone", "service", "status", "created_at")
    list_display_links = ("full_name",)
    list_editable = ("status",)
    list_filter = ("service", "status", "created_at")
    search_fields = ("full_name", "phone", "website_url")
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


class ProjectUpdateInline(admin.StackedInline):
    model = ProjectUpdate
    extra = 0
    fields = ("title", "message", "progress", "is_visible", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ClientProject)
class ClientProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "service", "status", "progress", "target_date", "updated_at")
    list_editable = ("status", "progress")
    list_filter = ("status", "service")
    search_fields = ("title", "client__username", "client__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = (ProjectUpdateInline,)
    fieldsets = (
        ("پروژه", {"fields": ("client", "contact_request", "title", "service")}),
        ("پیشرفت", {"fields": ("status", "progress", "target_date")}),
        ("زمان‌بندی", {"fields": ("created_at", "updated_at")}),
    )
