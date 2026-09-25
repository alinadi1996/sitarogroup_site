import re

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase
from django.urls import reverse

from blog.models import Post
from portfolio.models import Project
from tools.models import Tool

from .analysis import analyze_content
from .models import SiteSEOSettings, StaticPageSEO
from .services import (get_canonical_url, get_meta_description, get_page_seo,
                       get_robots_directive, get_schema_data, get_seo_title)


class SEOServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="writer", email="writer@example.com", password="test-password-123"
        )
        self.request = RequestFactory().get("/blog/1/")
        self.post = Post.objects.create(title="عنوان نوشته", slug="post-one", content="متن آغاز مقاله",
                                        author=self.user)

    def test_title_description_and_canonical_precedence(self):
        self.assertEqual(get_seo_title(self.post), "عنوان نوشته")
        self.assertIn("متن آغاز مقاله", get_meta_description(self.post))
        self.assertEqual(get_canonical_url(self.post, self.request),
                         "https://sitarogroup.ir" + self.post.get_absolute_url())
        self.post.seo_title = "عنوان اختصاصی"
        self.post.meta_description = "توضیح اختصاصی"
        self.post.canonical_url = "https://example.com/original/"
        self.assertEqual(get_seo_title(self.post), "عنوان اختصاصی")
        self.assertEqual(get_meta_description(self.post), "توضیح اختصاصی")
        self.assertEqual(get_canonical_url(self.post, self.request), "https://example.com/original/")

    def test_robots_and_noindex_skip_page_schema(self):
        self.post.robots_index = False
        self.post.robots_follow = False
        self.assertEqual(get_robots_directive(self.post), "noindex, nofollow")
        self.assertEqual(get_schema_data(self.post, self.request), [])

    def test_blog_schema_uses_real_values(self):
        schema = get_schema_data(self.post, self.request)[0]
        self.assertEqual(schema["@type"], "BlogPosting")
        self.assertEqual(schema["headline"], self.post.title)
        self.assertEqual(schema["author"]["name"], str(self.user))
        self.assertIn("datePublished", schema)
        self.assertEqual(schema["mainEntityOfPage"], "https://sitarogroup.ir" + self.post.get_absolute_url())
        self.assertNotIn("aggregateRating", schema)

    def test_project_breadcrumb_uses_existing_archive(self):
        project = Project.objects.create(title="پروژه واقعی", slug="real-project", industry="وب",
            summary="خلاصه پروژه", cover="portfolio/covers/example.webp", cover_alt="نمای پروژه",
            introduction="معرفی", challenge="مسئله", solution="راه‌حل", completed_work="طراحی",
            is_published=True)
        schema = get_schema_data(project, self.request)
        self.assertEqual(schema[0]["@type"], "BreadcrumbList")
        self.assertEqual(schema[0]["itemListElement"][0]["item"],
                         "https://sitarogroup.ir" + reverse("portfolio:project_list"))
        self.assertEqual(schema[1]["@type"], "CreativeWork")
        self.assertNotIn("review", schema[1])

    def test_custom_schema_validation_and_safe_render(self):
        self.post.schema_mode = "custom"
        self.post.custom_schema = {"@context": "https://schema.org", "@type": "Article",
                                   "headline": "</script><script>alert(1)</script>"}
        self.post.full_clean()
        self.post.save()
        response = self.client.get(self.post.get_absolute_url())
        self.assertContains(response, "\\u003C/script\\u003E")
        self.assertNotContains(response, "</script><script>alert(1)</script>")
        self.assertEqual(get_schema_data(self.post, self.request)[0]["@type"], "Article")
        self.post.custom_schema = {"headline": "فاقد نوع"}
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_static_page_uniqueness_and_site_schema(self):
        StaticPageSEO.objects.create(page_key="home", seo_title="خانه سیتارو")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StaticPageSEO.objects.create(page_key="home")
        seo = get_page_seo("home", RequestFactory().get("/"))
        self.assertEqual(seo["title"], "خانه سیتارو")
        self.assertEqual({item["@type"] for item in seo["schema"]}, {"Organization", "WebSite"})
        self.assertTrue(SiteSEOSettings.objects.filter(pk=1).exists())

    def test_editorial_checklist_reports_gaps_without_score(self):
        checks = analyze_content(self.post)
        labels = {item["label"]: item for item in checks}
        self.assertFalse(labels["توضیح متای اختصاصی"]["ok"])
        self.assertFalse(labels["عبارت کلیدی هدف"]["ok"])
        self.assertFalse(labels["تصویر شاخص"]["ok"])
        self.assertFalse(labels["تیتر H2"]["ok"])
        self.assertNotIn("score", checks[0])

    def test_head_renders_each_tag_once_without_keywords(self):
        for url in (reverse("home"), self.post.get_absolute_url(), reverse("leads:contact")):
            with self.subTest(url=url):
                head = self.client.get(url).content.decode().split("</head>", 1)[0]
                self.assertEqual(len(re.findall(r"<title>", head)), 1)
                self.assertEqual(len(re.findall(r'<meta name="description"', head)), 1)
                self.assertEqual(len(re.findall(r'<link rel="canonical"', head)), 1)
                self.assertEqual(len(re.findall(r'<meta name="robots"', head)), 1)
                self.assertNotIn('name="keywords"', head)

    def test_active_tool_has_schema_but_disabled_tool_does_not(self):
        tool, _ = Tool.objects.get_or_create(slug="schema-generator", defaults={
            "title": "ابزار آزمایشی", "short_description": "توضیح واقعی",
            "status": Tool.Status.ACTIVE,
        })
        tool.status = Tool.Status.ACTIVE
        self.assertIn("WebApplication", [item["@type"] for item in get_schema_data(tool, self.request)])
        tool.status = Tool.Status.DISABLED
        self.assertEqual(get_schema_data(tool, self.request), [])

    def test_admin_json_error_is_persian_and_singleton_cannot_be_added(self):
        self.request.user = get_user_model().objects.create_superuser(
            username="seo-admin", email="seo-admin@example.com", password="test-password-123"
        )
        form_class = admin.site._registry[Post].get_form(self.request)
        with self.assertRaisesMessage(ValidationError, "ساختار JSON معتبر نیست"):
            form_class.base_fields["custom_schema"].clean("{broken json")
        self.assertFalse(admin.site._registry[SiteSEOSettings].has_add_permission(self.request))

    def test_static_page_admin_excludes_existing_page_key(self):
        StaticPageSEO.objects.create(page_key="home")
        self.request.user = get_user_model().objects.create_superuser(
            username="seo-admin", email="seo-admin@example.com", password="test-password-123"
        )
        form_class = admin.site._registry[StaticPageSEO].get_form(self.request)
        values = [value for value, _ in form_class.base_fields["page_key"].choices]
        self.assertNotIn("home", values)
        self.assertIn("contact", values)

    def test_admin_displays_read_only_editorial_checklist(self):
        manager = get_user_model().objects.create_superuser(
            username="seo-manager", email="seo-manager@example.com", password="test-password-123"
        )
        self.client.force_login(manager)
        response = self.client.get(reverse("admin:blog_post_change", args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بررسی داخلی SEO")
        self.assertContains(response, "نیازمند بررسی")
        self.assertNotContains(response, "امتیاز سئو گوگل")
