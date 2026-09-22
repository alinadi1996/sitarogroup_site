from django.urls import path

from .views import (
    ImageConvertView, SchemaGeneratorView, SerpPreviewView,
    SitemapRobotsGeneratorView, ToolIndexView, ToolLaunchView, WebsiteAnalyzerView,
)

app_name = "tools"

urlpatterns = [
    path("", ToolIndexView.as_view(), name="index"),
    path("website-analyzer/", WebsiteAnalyzerView.as_view(), name="website_analyzer"),
    path("serp-preview/", SerpPreviewView.as_view(), name="serp_preview"),
    path("image-converter/", ImageConvertView.as_view(), name="image_converter"),
    path("schema-generator/", SchemaGeneratorView.as_view(), name="schema_generator"),
    path(
        "sitemap-robots-generator/",
        SitemapRobotsGeneratorView.as_view(),
        name="sitemap_robots_generator",
    ),
    path("<slug:slug>/", ToolLaunchView.as_view(), name="launch"),
]
