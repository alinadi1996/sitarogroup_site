from django.urls import path

from .views import SignUpView, SitaroLoginView, SitaroLogoutView, ProfileView

app_name = 'accounts'

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
]
