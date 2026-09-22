from django.urls import path

from pages.views import HomePageView
from pages.support import support_answer

urlpatterns = [
    path('support/answer/', support_answer, name='support_answer'),
    path('', HomePageView.as_view(), name="home"),
]
