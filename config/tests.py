from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from leads.models import ClientProject, ContactRequest
from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="test-password-123"
        )
        self.client.force_login(self.user)

    def test_unfold_site_and_dashboard(self):
        self.assertIsInstance(admin.site, UnfoldAdminSite)
        self.assertIsInstance(admin.site._registry[ContactRequest], ModelAdmin)

        ContactRequest.objects.create(
            full_name="مشتری نمونه",
            phone="09120000000",
            service=ContactRequest.Service.WEB_DESIGN,
            project_description="سایت جدید",
        )
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "نمای کلی سیتارو")
        self.assertContains(response, "مشتری نمونه")
        self.assertContains(response, "درخواست‌های جدید")

    def test_existing_admin_forms_render(self):
        project = ClientProject.objects.create(
            client=self.user,
            title="پروژه آزمایشی",
            service=ContactRequest.Service.WEB_DESIGN,
        )
        for name in (
            "admin:accounts_customuser_add",
            "admin:auth_group_add",
            "admin:leads_contactrequest_add",
            "admin:leads_clientproject_add",
            "admin:portfolio_project_add",
            "admin:tools_tool_add",
        ):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("admin:accounts_customuser_change", args=[self.user.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("admin:leads_clientproject_change", args=[project.pk])).status_code,
            200,
        )

    def test_dashboard_respects_model_permissions(self):
        staff = get_user_model().objects.create_user(
            username="staff", email="staff@example.com", password="test-password-123", is_staff=True
        )
        staff.user_permissions.add(Permission.objects.get(codename="view_contactrequest"))
        ContactRequest.objects.create(
            full_name="درخواست مجاز",
            phone="09120000000",
            service=ContactRequest.Service.WEB_DESIGN,
            project_description="سایت جدید",
        )
        ClientProject.objects.create(
            client=self.user,
            title="پروژه محرمانه",
            service=ContactRequest.Service.WEB_DESIGN,
        )
        self.client.force_login(staff)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "درخواست مجاز")
        self.assertNotContains(response, "پروژه محرمانه")
        self.assertNotContains(response, "پروژه‌های فعال")
        self.assertContains(response, reverse("admin:leads_contactrequest_changelist"))
        self.assertNotContains(response, reverse("admin:leads_clientproject_changelist"))

    def test_request_changelist_filters_and_search(self):
        ContactRequest.objects.create(
            full_name="درخواست تازه",
            phone="09120000000",
            service=ContactRequest.Service.WEB_DESIGN,
            project_description="سایت جدید",
        )
        ContactRequest.objects.create(
            full_name="درخواست ردشده",
            phone="09120000001",
            service=ContactRequest.Service.SEO_PERFORMANCE,
            project_description="سئو",
            status=ContactRequest.Status.REJECTED,
        )
        url = reverse("admin:leads_contactrequest_changelist")

        filtered = self.client.get(url, {"status__exact": ContactRequest.Status.NEW})
        self.assertEqual(filtered.status_code, 200)
        self.assertContains(filtered, "درخواست تازه")
        self.assertNotContains(filtered, "درخواست ردشده")

        searched = self.client.get(url, {"q": "09120000001"})
        self.assertEqual(searched.status_code, 200)
        self.assertContains(searched, "درخواست ردشده")
        self.assertNotContains(searched, "درخواست تازه")
