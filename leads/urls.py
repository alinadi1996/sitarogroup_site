from django.urls import path

from .views import ContactRequestView

app_name = "leads"

urlpatterns = [
    path("", ContactRequestView.as_view(), name="contact"),
]

