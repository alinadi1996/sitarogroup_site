from django.contrib import admin
from django.test import TestCase
from django.urls import resolve, reverse

from .models import Tool, ToolCategory


class ToolsPublicPagesTests(TestCase):
    def setUp(self):
        Tool.objects.all().delete()
        ToolCategory.objects.all().delete()
        self.category = ToolCategory.objects.create(
            title="سئو فنی", slug="technical-seo-test", order=10, is_active=True
        )

    def create_tool(self, **overrides):
        defaults = {
            "title": "ابزار آزمون",
            "slug": "test-tool",
            "short_description": "توضیح واقعی و کوتاه برای ابزار آزمون.",
            "category": self.category,
            "status": Tool.Status.COMING_SOON,
            "order": 10,
        }
        defaults.update(overrides)
        return Tool.objects.create(**defaults)

    def test_index_page_opens(self):
        response = self.client.get(reverse("tools:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ابزارهای رایگان")

    def test_active_and_coming_soon_are_visible_but_disabled_is_hidden(self):
        active = self.create_tool(title="ابزار فعال", slug="active-tool", status=Tool.Status.ACTIVE)
        coming = self.create_tool(title="ابزار آینده", slug="future-tool", order=20)
        disabled = self.create_tool(
            title="ابزار غیرفعال", slug="disabled-tool", status=Tool.Status.DISABLED, order=30
        )

        response = self.client.get(reverse("tools:index"))

        self.assertContains(response, active.title)
        self.assertContains(response, coming.title)
        self.assertNotContains(response, disabled.title)

    def test_featured_tool_uses_featured_section(self):
        featured = self.create_tool(is_featured=True)
        response = self.client.get(reverse("tools:index"))
        self.assertEqual(response.context["featured_tool"], featured)
        self.assertContains(response, "featured-tool")

    def test_tools_keep_model_ordering(self):
        second = self.create_tool(title="دوم", slug="second", order=20)
        first = self.create_tool(title="اول", slug="first", order=10)
        response = self.client.get(reverse("tools:index"))
        self.assertEqual(list(response.context["tools"]), [first, second])

    def test_empty_state_renders_without_error(self):
        response = self.client.get(reverse("tools:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ابزارهای Sitaro در حال آماده‌سازی هستند.")

    def test_header_and_contact_links_use_named_urls(self):
        response = self.client.get(reverse("tools:index"))
        self.assertContains(response, reverse("tools:index"))
        self.assertContains(response, reverse("leads:contact"))
        self.assertContains(response, "data-tools-toggle")
        self.assertContains(response, "data-mobile-tools-toggle")

    def test_header_context_excludes_disabled_and_inactive_category_tools(self):
        self.create_tool(title="شاخص", slug="featured", is_featured=True, order=50)
        self.create_tool(title="فعال", slug="active", status=Tool.Status.ACTIVE, order=10)
        self.create_tool(title="مخفی", slug="hidden", status=Tool.Status.DISABLED, order=1)
        inactive_category = ToolCategory.objects.create(
            title="دسته خاموش", slug="inactive", order=20, is_active=False
        )
        self.create_tool(title="دسته غیرفعال", slug="inactive-category", category=inactive_category)

        response = self.client.get(reverse("tools:index"))
        header_tools = list(response.context["header_tools"])

        self.assertEqual(header_tools[0].slug, "featured")
        self.assertNotIn("hidden", [tool.slug for tool in header_tools])
        self.assertNotIn("inactive-category", [tool.slug for tool in header_tools])
        self.assertLessEqual(len(header_tools), 5)

    def test_admin_registration(self):
        self.assertTrue(admin.site.is_registered(Tool))
        self.assertTrue(admin.site.is_registered(ToolCategory))

    def test_get_absolute_url_only_returns_a_resolvable_url_for_active_tools(self):
        active = self.create_tool(slug="ready", status=Tool.Status.ACTIVE)
        coming = self.create_tool(slug="later", order=20)
        disabled = self.create_tool(slug="off", status=Tool.Status.DISABLED, order=30)

        self.assertEqual(resolve(active.get_absolute_url()).url_name, "launch")
        self.assertEqual(coming.get_absolute_url(), "")
        self.assertEqual(disabled.get_absolute_url(), "")

        response = self.client.get(active.get_absolute_url())
        self.assertRedirects(response, f"{reverse('tools:index')}#tool-ready", fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("tools:launch", kwargs={"slug": coming.slug})).status_code, 404)

