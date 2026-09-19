from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ContactRequestForm


class ContactRequestView(FormView):
    template_name = "leads/contact.html"
    form_class = ContactRequestForm
    success_url = reverse_lazy("leads:contact")

    def form_valid(self, form):
        form.save()
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

