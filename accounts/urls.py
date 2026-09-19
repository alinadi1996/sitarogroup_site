from django.urls import path

from .views import SignUpView, SitaroLoginView, SitaroLogoutView, ProfileView

app_name = 'accounts'

urlpatterns = [
    path('login/', SitaroLoginView.as_view(), name='login'),
    path('logout/', SitaroLogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
