from django.urls import path

from .views import ProjectDetailView, ProjectListView

app_name = "portfolio"

urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("<str:slug>/", ProjectDetailView.as_view(), name="project_detail"),
]
