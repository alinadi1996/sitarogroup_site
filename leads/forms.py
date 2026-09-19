import re

from django import forms
from django.core.exceptions import ValidationError

from .models import ContactRequest


PHONE_PATTERN = re.compile(r"^(?:09\d{9}|\+989\d{9})$")
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


class ContactRequestForm(forms.ModelForm):
    company_website = forms.CharField(
        required=False,
        label="وب‌سایت شرکت",
        widget=forms.TextInput(
            attrs={
                "class": "contact-honeypot",
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )

    class Meta:
        model = ContactRequest
        fields = (
            "full_name",
            "phone",
            "service",
            "project_description",
            "website_url",
            "estimated_budget",
            "preferred_contact_method",
        )
        labels = {
            "full_name": "نام و نام خانوادگی",
            "phone": "شماره موبایل",
            "service": "نوع خدمت موردنیاز",
            "project_description": "درباره پروژه",
            "website_url": "آدرس وب‌سایت فعلی",
            "estimated_budget": "بودجه تقریبی",
            "preferred_contact_method": "روش ارتباط ترجیحی",
        }
        widgets = {
            "full_name": forms.TextInput(
                attrs={"autocomplete": "name", "placeholder": "نام فرد مسئول پروژه"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "dir": "ltr",
                    "placeholder": "09xxxxxxxxx یا +989xxxxxxxxx",
                }
            ),
            "service": forms.Select(),
            "project_description": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": "هدف، نیاز اصلی و وضعیت فعلی پروژه را کوتاه توضیح دهید.",
                }
            ),
            "website_url": forms.URLInput(
                attrs={
                    "autocomplete": "url",
                    "inputmode": "url",
                    "dir": "ltr",
                    "placeholder": "https://example.com",
                }
            ),
            "estimated_budget": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "placeholder": "در صورت تمایل، بازه بودجه را بنویسید.",
                }
            ),
            "preferred_contact_method": forms.Select(),
        }
        error_messages = {
            "full_name": {"required": "لطفاً نام و نام خانوادگی را وارد کنید."},
            "phone": {"required": "لطفاً شماره موبایل را وارد کنید."},
            "service": {"required": "لطفاً نوع خدمت موردنیاز را انتخاب کنید."},
            "project_description": {"required": "لطفاً توضیح کوتاهی درباره پروژه بنویسید."},
            "website_url": {"invalid": "آدرس وب‌سایت معتبر نیست؛ آن را همراه با http یا https وارد کنید."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].choices = [("", "انتخاب خدمت")] + list(ContactRequest.Service.choices)
        self.fields["preferred_contact_method"].required = False
        self.fields["preferred_contact_method"].choices = list(ContactRequest.ContactMethod.choices)
        self.fields["preferred_contact_method"].initial = ContactRequest.ContactMethod.PHONE

        for name, field in self.fields.items():
            if name == "company_website":
                continue
            field.widget.attrs["class"] = "contact-input"
            field.widget.attrs["aria-describedby"] = f"id_{name}_help id_{name}_errors"

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()
        if not value:
            raise ValidationError("لطفاً نام و نام خانوادگی را وارد کنید.")
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].translate(PERSIAN_DIGITS)
        value = re.sub(r"[\s\-()]", "", value)
        if not PHONE_PATTERN.fullmatch(value):
            raise ValidationError("شماره موبایل باید به شکل 09xxxxxxxxx یا +989xxxxxxxxx باشد.")
        return value

    def clean_project_description(self):
        value = self.cleaned_data["project_description"].strip()
        if not value:
            raise ValidationError("لطفاً توضیح کوتاهی درباره پروژه بنویسید.")
        return value

    def clean_company_website(self):
        value = self.cleaned_data.get("company_website", "")
        if value:
            raise ValidationError("ثبت فرم انجام نشد. لطفاً دوباره تلاش کنید.")
        return value

    def clean_preferred_contact_method(self):
        return self.cleaned_data.get("preferred_contact_method") or ContactRequest.ContactMethod.PHONE

