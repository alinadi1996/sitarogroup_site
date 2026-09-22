from django.urls import path

from .views import ToolIndexView, ToolLaunchView

app_name = "tools"

urlpatterns = [
    path("", ToolIndexView.as_view(), name="index"),
    path("<slug:slug>/", ToolLaunchView.as_view(), name="launch"),
]
