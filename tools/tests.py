from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse
from io import BytesIO
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image

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

    def test_serp_preview_page_and_active_tool_link(self):
        serp_preview = self.create_tool(
            title="پیش‌نمایش نتیجه گوگل",
            slug="serp-preview",
            status=Tool.Status.ACTIVE,
        )

        response = self.client.get(reverse("tools:serp_preview"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tools/serp_preview.html")
        self.assertContains(response, "پیش‌نمایش نتیجه گوگل")
        self.assertContains(response, reverse("tools:index"))
        self.assertContains(response, reverse("leads:contact"))
        self.assertEqual(serp_preview.get_absolute_url(), reverse("tools:serp_preview"))

    def test_serp_preview_card_and_header_use_the_real_tool_url(self):
        serp_preview = self.create_tool(
            title="پیش‌نمایش نتیجه گوگل",
            slug="serp-preview",
            status=Tool.Status.ACTIVE,
        )
        coming = self.create_tool(title="ابزار بعدی", slug="next-tool", order=20)

        response = self.client.get(reverse("tools:index"))

        self.assertContains(response, serp_preview.get_absolute_url())
        self.assertContains(response, "data-tools-toggle")
        self.assertContains(response, "به‌زودی")
        self.assertEqual(coming.get_absolute_url(), "")

    def test_schema_generator_page_and_active_tool_link(self):
        schema_generator = self.create_tool(
            title="ساخت اسکیما JSON-LD",
            slug="schema-generator",
            status=Tool.Status.ACTIVE,
        )

        response = self.client.get(reverse("tools:schema_generator"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tools/schema_generator.html")
        self.assertContains(response, "ساخت اسکیما JSON-LD")
        self.assertContains(response, reverse("tools:index"))
        self.assertContains(response, reverse("leads:contact"))
        self.assertEqual(schema_generator.get_absolute_url(), reverse("tools:schema_generator"))

    def test_schema_generator_card_and_header_use_the_real_tool_url(self):
        schema_generator = self.create_tool(
            title="ساخت اسکیما JSON-LD",
            slug="schema-generator",
            status=Tool.Status.ACTIVE,
        )
        coming = self.create_tool(title="ابزار بعدی", slug="later-tool", order=20)

        response = self.client.get(reverse("tools:index"))

        self.assertContains(response, schema_generator.get_absolute_url())
        self.assertContains(response, "data-tools-toggle")
        self.assertContains(response, "به‌زودی")
        self.assertEqual(coming.get_absolute_url(), "")
    def test_active_image_converter_links_directly_to_converter(self):
        converter = self.create_tool(slug="image-optimizer", status=Tool.Status.ACTIVE)

        self.assertEqual(converter.get_absolute_url(), reverse("tools:image_converter"))

    def test_active_website_analyzer_links_directly_to_analyzer(self):
        analyzer = self.create_tool(slug="website-analyzer", status=Tool.Status.ACTIVE)

        self.assertEqual(analyzer.get_absolute_url(), reverse("tools:website_analyzer"))


class ImageConverterTests(TestCase):
    @staticmethod
    def image_upload(name="sample.png", color=(255, 0, 0, 255)):
        image = Image.new("RGBA", (12, 12), color)
        content = BytesIO()
        image.save(content, "PNG")
        return SimpleUploadedFile(name, content.getvalue(), content_type="image/png")

    def test_converter_page_opens(self):
        response = self.client.get(reverse("tools:image_converter"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تبدیل تصویر")

    def test_single_image_converts_to_webp(self):
        response = self.client.post(
            reverse("tools:image_converter"),
            {"image": self.image_upload(), "output_format": "webp"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/webp")
        self.assertIn('filename="sample.webp"', response["Content-Disposition"])
        self.assertEqual(Image.open(BytesIO(response.content)).format, "WEBP")

    def test_zip_images_convert_to_requested_format(self):
        archive_content = BytesIO()
        with ZipFile(archive_content, "w", ZIP_DEFLATED) as archive:
            archive.writestr("first.png", self.image_upload().read())
            archive.writestr("nested/second.png", self.image_upload("second.png").read())
        upload = SimpleUploadedFile("images.zip", archive_content.getvalue(), content_type="application/zip")

        response = self.client.post(
            reverse("tools:image_converter"), {"image": upload, "output_format": "jpeg"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        with ZipFile(BytesIO(response.content)) as result:
            self.assertEqual(sorted(result.namelist()), ["01-first.jpg", "02-second.jpg"])
            self.assertEqual(Image.open(BytesIO(result.read("01-first.jpg"))).format, "JPEG")

    def test_invalid_file_returns_form_error(self):
        upload = SimpleUploadedFile("not-an-image.txt", b"not an image", content_type="text/plain")
        response = self.client.post(
            reverse("tools:image_converter"), {"image": upload, "output_format": "png"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "فایل تصویر معتبر نیست", status_code=400)


class WebsiteAnalyzerTests(TestCase):
    def test_analyzer_page_opens(self):
        response = self.client.get(reverse("tools:website_analyzer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تحلیل سایت")

    @patch("tools.views.fetch_page_speed")
    @patch("tools.views.inspect_website")
    @patch("tools.views.validate_public_url", return_value="https://example.com")
    def test_analyzer_renders_website_and_pagespeed_results(self, validate_url, inspect, page_speed):
        inspect.return_value = {
            "final_url": "https://example.com",
            "status_code": 200,
            "title": "Example",
            "description": "Example description",
            "h1_count": 1,
        }
        page_speed.return_value = (
            {"score": 92, "first_contentful_paint": "0.8 s", "largest_contentful_paint": "1.4 s", "total_blocking_time": "0 ms", "cumulative_layout_shift": "0"},
            None,
        )

        response = self.client.post(reverse("tools:website_analyzer"), {"url": "https://example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Example description")
        self.assertContains(response, "92")
        page_speed.assert_called_once_with("https://example.com")

    @patch("tools.views.validate_public_url", side_effect=ValueError("آدرس‌های محلی یا خصوصی قابل بررسی نیستند."))
    def test_private_address_is_rejected(self, validate_url):
        response = self.client.post(reverse("tools:website_analyzer"), {"url": "http://127.0.0.1"})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "آدرس‌های محلی یا خصوصی", status_code=400)

