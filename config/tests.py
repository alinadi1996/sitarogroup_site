from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.test import override_settings
from django.core.cache import cache
from unittest.mock import patch

from leads.models import ClientProject, ContactRequest
from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite
from config.admin_seo import search_console_status
from blog.models import Post


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

    @patch("config.admin_seo.public_site_status", return_value={"reachable": True, "http_status": 200})
    @patch("config.admin_seo.search_console_status", return_value={"state": "unconfigured"})
    def test_seo_overview_shows_real_content_and_unconfigured_connection(self, _gsc, _public):
        Post.objects.create(title="آموزش سئو", slug="seo-guide", content="متن",
                            author=self.user)
        response = self.client.get(reverse("admin:seo_overview"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "آموزش سئو")
        self.assertContains(response, "همهٔ نوشته‌ها")
        self.assertContains(response, "اتصال هنوز فعال نیست")
        self.assertContains(response, "/robots.txt")
        self.assertContains(response, "/sitemap.xml")
        self.assertContains(response, "sitaro-logo.svg")

    @patch("config.admin_seo.public_site_status", return_value={"reachable": False, "http_status": None})
    @patch("config.admin_seo.search_console_status", return_value={"state": "connected", "clicks": 12,
           "impressions": 200, "ctr": 6.0, "position": 4.2, "start_date": None, "end_date": None})
    def test_seo_overview_connected_metrics_and_site_warning(self, _gsc, _public):
        response = self.client.get(reverse("admin:seo_overview"))
        self.assertContains(response, "اتصال برقرار است")
        self.assertContains(response, "در دسترس نیست")
        self.assertContains(response, "200")

    def test_seo_overview_is_superuser_only(self):
        staff = get_user_model().objects.create_user(
            username="seo-staff", email="seo@example.com", password="test-password-123", is_staff=True
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("admin:seo_overview")).status_code, 403)

    @override_settings(SITARO_GSC_CREDENTIALS_FILE="")
    def test_search_console_does_not_claim_connection_without_credentials(self):
        self.assertEqual(search_console_status()["state"], "unconfigured")

    def test_public_seo_routes(self):
        robots = self.client.get(reverse("robots_txt"))
        sitemap = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Sitemap:")
        self.assertEqual(sitemap.status_code, 200)

    @override_settings(SITARO_GSC_SITE_URL="https://test-sitaro.example/",
                       SITARO_GSC_CREDENTIALS_FILE="private-service-account.json")
    @patch("config.admin_seo.Path.is_file", return_value=True)
    @patch("google.oauth2.service_account.Credentials.from_service_account_file")
    @patch("google.auth.transport.requests.AuthorizedSession")
    def test_search_console_uses_read_only_scope_and_real_response(self, session_class, credentials, _file):
        cache.delete("sitaro-gsc-https://test-sitaro.example/")
        response = session_class.return_value.post.return_value
        response.json.return_value = {"rows": [{"clicks": 12, "impressions": 200,
                                                  "ctr": 0.06, "position": 4.2}]}

        result = search_console_status()

        self.assertEqual(result["state"], "connected")
        self.assertEqual(result["clicks"], 12)
        self.assertEqual(result["ctr"], 6.0)
        self.assertIn("webmasters.readonly", credentials.call_args.kwargs["scopes"][0])
        self.assertIn("https%3A%2F%2Ftest-sitaro.example%2F", session_class.return_value.post.call_args.args[0])
