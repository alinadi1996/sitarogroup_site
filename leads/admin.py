from django.contrib import admin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "service", "status", "created_at")
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

