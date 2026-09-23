"""Small, permission-aware overview for the internal Unfold dashboard."""

from django.urls import reverse

from blog.models import Post
from leads.models import ClientProject, ContactRequest
from portfolio.models import Project


def dashboard_callback(request, context):
    user = request.user
    metrics = []
    recent_requests = []
    recent_projects = []

    def can_view(app_label, model_name):
        return user.has_perm(f"{app_label}.view_{model_name}") or user.has_perm(
            f"{app_label}.change_{model_name}"
        )

    show_requests = can_view("leads", "contactrequest")
    show_projects = can_view("leads", "clientproject")

    if show_requests:
        metrics.append({
            "label": "درخواست‌های جدید",
            "value": ContactRequest.objects.filter(status=ContactRequest.Status.NEW).count(),
            "url": reverse("admin:leads_contactrequest_changelist"),
            "accent": "mint",
        })
        recent_requests = list(ContactRequest.objects.order_by("-created_at")[:5])

    if show_projects:
        metrics.append({
            "label": "پروژه‌های فعال",
            "value": ClientProject.objects.exclude(status=ClientProject.Status.COMPLETED).count(),
            "url": reverse("admin:leads_clientproject_changelist"),
            "accent": "blue",
        })
        recent_projects = list(ClientProject.objects.select_related("client").order_by("-updated_at")[:5])

    if can_view("blog", "post"):
        metrics.append({
            "label": "نوشته‌های وبلاگ",
            "value": Post.objects.count(),
            "url": reverse("admin:blog_post_changelist"),
            "accent": "amber",
        })

    if can_view("portfolio", "project"):
        metrics.append({
            "label": "نمونه‌کارهای منتشرشده",
            "value": Project.objects.filter(is_published=True).count(),
            "url": reverse("admin:portfolio_project_changelist"),
            "accent": "mint",
        })

    context.update({
        "dashboard_metrics": metrics,
        "recent_requests": recent_requests,
        "recent_projects": recent_projects,
        "show_requests": show_requests,
        "show_projects": show_projects,
    })
    return context
