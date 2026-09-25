from django.views.generic import DetailView, ListView

from .models import Project
from seo.services import build_seo


class ProjectListView(ListView):
    model = Project
    template_name = "portfolio/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.published()


class ProjectDetailView(DetailView):
    model = Project
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.published().prefetch_related("gallery_images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo"] = build_seo(self.object, self.request)
        return context
