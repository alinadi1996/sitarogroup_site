from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import DetailView
from django.db.models import Prefetch

from leads.models import ProjectUpdate

from .forms import CustomUserCreationForm, PersianAuthenticationForm


class SitaroLoginView(LoginView):
    authentication_form = PersianAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class SitaroLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'registration/signup.html'

class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'registration/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_projects"] = self.request.user.client_projects.prefetch_related(
            Prefetch("updates", queryset=ProjectUpdate.objects.filter(is_visible=True))
        )
        return context
