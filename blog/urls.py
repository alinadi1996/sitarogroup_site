from django.urls import path

from . import views
from .views import BlogListView, BlogDetailView

app_name = "blog"

urlpatterns = [
    path('' , BlogListView.as_view() , name='blog_list'),
    path('<int:pk>/' , BlogDetailView.as_view() , name='blog_detail'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]
