from django.urls import path

from .views import ImageConvertView, ToolIndexView, ToolLaunchView, WebsiteAnalyzerView

app_name = "tools"

urlpatterns = [
    path("", ToolIndexView.as_view(), name="index"),
    path("image-converter/", ImageConvertView.as_view(), name="image_converter"),
    path("website-analyzer/", WebsiteAnalyzerView.as_view(), name="website_analyzer"),
    path("<slug:slug>/", ToolLaunchView.as_view(), name="launch"),
]
