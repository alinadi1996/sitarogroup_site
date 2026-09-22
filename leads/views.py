from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactRequestForm
from .models import ClientProject


class ContactRequestView(FormView):
    template_name = "leads/contact.html"
    form_class = ContactRequestForm
    success_url = reverse_lazy("leads:contact")

    def form_valid(self, form):
        contact_request = form.save(commit=False)
        if self.request.user.is_authenticated:
            contact_request.user = self.request.user
        contact_request.save()
        if contact_request.user_id:
            ClientProject.objects.get_or_create(
                contact_request=contact_request,
                defaults={
                    "client": contact_request.user,
                    "title": f"پروژه {contact_request.get_service_display()}",
                    "service": contact_request.service,
                },
            )
        messages.success(
            self.request,
            "درخواست شما با موفقیت ثبت شد. برای هماهنگی اولیه با شما تماس می‌گیریم.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "contact_phone": getattr(settings, "SITARO_CONTACT_PHONE", ""),
                "whatsapp_url": getattr(settings, "SITARO_WHATSAPP_URL", ""),
                "telegram_url": getattr(settings, "SITARO_TELEGRAM_URL", ""),
            }
        )
        return context
