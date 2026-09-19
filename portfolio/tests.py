from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from .models import Project


class PortfolioPublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published = Project.objects.create(
            title="پروژه آزمون",
            slug="project-test",
            industry="حوزه آزمون",
            summary="خلاصه پروژه برای آزمون ساختار صفحه.",
            cover_alt="نمای پروژه آزمون",
            introduction="معرفی پروژه",
            challenge="شرح مسئله",
            solution="شرح راه‌حل",
            completed_work="طراحی تجربه کاربری\nتوسعه رابط",
            is_published=True,
        )
        Project.objects.create(
            title="پیش‌نویس",
            slug="draft-project",
            industry="حوزه آزمون",
            summary="این پروژه نباید عمومی باشد.",
            cover_alt="نمای پیش‌نویس",
            introduction="معرفی",
            challenge="مسئله",
            solution="راه‌حل",
            completed_work="طراحی",
            is_published=False,
        )

    def test_list_only_shows_published_projects(self):
        response = self.client.get(reverse("portfolio:project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published.title)
        self.assertNotContains(response, "پیش‌نویس")

    def test_detail_has_required_sections_and_optional_fields_stay_hidden(self):
        response = self.client.get(self.published.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "معرفی پروژه")
        self.assertContains(response, "مسئله")
        self.assertContains(response, "راه‌حل")
        self.assertContains(response, "کارهای انجام‌شده")
        self.assertNotContains(response, "05 / OUTCOME")
        self.assertNotContains(response, "مشاهده سایت")

    def test_draft_detail_returns_404(self):
        response = self.client.get(reverse("portfolio:project_detail", kwargs={"slug": "draft-project"}))
        self.assertEqual(response.status_code, 404)

    def test_project_is_available_in_existing_admin(self):
        self.assertTrue(admin.site.is_registered(Project))
