from django.urls import path

from .views import ProfileEditView, ProfileView, SignUpView, SitaroLoginView, SitaroLogoutView

app_name = 'accounts'

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('edit/', ProfileEditView.as_view(), name='profile_edit'),
]
