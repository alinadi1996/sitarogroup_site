from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .models import Tool


class ToolIndexView(ListView):
    model = Tool
    template_name = "tools/index.html"
    context_object_name = "tools"

    def get_queryset(self):
        return Tool.objects.public().select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visible_tools = list(context["tools"])
        featured_tool = next((tool for tool in visible_tools if tool.is_featured), None)
        context["featured_tool"] = featured_tool
        context["tools"] = [tool for tool in visible_tools if tool != featured_tool]
        context["visible_tool_count"] = len(visible_tools)
        return context


class ToolLaunchView(View):
    """Stable future tool endpoint; no tool logic is implemented at this stage."""

    def get(self, request, slug):
        tool = Tool.objects.public().filter(slug=slug, status=Tool.Status.ACTIVE).first()
        if tool is None:
            raise Http404("این ابزار در دسترس نیست.")
        return HttpResponseRedirect(f"{reverse('tools:index')}#tool-{tool.slug}")
