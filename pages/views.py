from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView

from portfolio.models import Project


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.published()[:4]
        return context


