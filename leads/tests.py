from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ContactRequest


class ContactRequestTests(TestCase):
    def setUp(self):
        self.url = reverse("leads:contact")
        self.valid_data = {
            "full_name": "کاربر آزمون",
            "phone": "09123456789",
            "service": ContactRequest.Service.WEB_DESIGN,
            "project_description": "برای طراحی و توسعه یک وب‌سایت اختصاصی نیاز به مشاوره دارم.",
            "website_url": "",
            "estimated_budget": "",
            "preferred_contact_method": ContactRequest.ContactMethod.PHONE,
            "company_website": "",
        }

    def test_contact_page_opens(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/contact.html")
        self.assertContains(response, "بیایید درباره")
        self.assertContains(response, "پروژه‌تان صحبت کنیم")

    def test_successful_submission_uses_post_redirect_get(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.url)
        self.assertEqual(ContactRequest.objects.count(), 1)

        refreshed = self.client.get(self.url)
        self.assertEqual(refreshed.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_success_message_is_shown_after_redirect(self):
        response = self.client.post(self.url, self.valid_data, follow=True)
        self.assertContains(
            response,
            "درخواست شما با موفقیت ثبت شد. برای هماهنگی اولیه با شما تماس می‌گیریم.",
        )

    def test_invalid_phone_is_rejected_and_value_is_preserved(self):
        data = {**self.valid_data, "phone": "12345"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "phone",
            "شماره موبایل باید به شکل 09xxxxxxxxx یا +989xxxxxxxxx باشد.",
        )
        self.assertContains(response, 'value="12345"')
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_both_supported_phone_formats_are_accepted(self):
        for phone in ("09123456789", "+989123456789"):
            with self.subTest(phone=phone):
                ContactRequest.objects.all().delete()
                response = self.client.post(self.url, {**self.valid_data, "phone": phone})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(ContactRequest.objects.get().phone, phone)

    def test_main_fields_are_required(self):
        for field_name in ("full_name", "phone", "service", "project_description"):
            with self.subTest(field=field_name):
                data = {**self.valid_data, field_name: ""}
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field_name, response.context["form"].errors)
                self.assertEqual(ContactRequest.objects.count(), 0)

    def test_honeypot_blocks_submission(self):
        response = self.client.post(
            self.url,
            {**self.valid_data, "company_website": "https://spam.example"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("company_website", response.context["form"].errors)
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_model_is_registered_and_visible_in_admin(self):
        self.assertTrue(admin.site.is_registered(ContactRequest))
        request = ContactRequest.objects.create(
            full_name="درخواست ادمین",
            phone="09121111111",
            service=ContactRequest.Service.SEO_PERFORMANCE,
            project_description="بررسی فنی وب‌سایت",
        )
        user = get_user_model().objects.create_superuser(
            username="admin-contact",
            email="admin-contact@example.test",
            password="strong-test-password",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("admin:leads_contactrequest_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, request.full_name)
        self.assertContains(response, request.phone)
