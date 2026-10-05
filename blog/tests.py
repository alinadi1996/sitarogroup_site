from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from blog.forms import PostAdminForm
from blog.rich_text import sanitize_rich_text


class RichTextTests(SimpleTestCase):
    def test_editor_keeps_formatting_and_strips_unsafe_markup(self):
        content = '<h2>عنوان</h2><p><strong>متن</strong> <a href="javascript:alert(1)" onclick="alert(2)">بد</a> <a href="https://example.com">خوب</a></p><img src=x onerror=alert(3)><script>alert(4)</script>'
        clean = sanitize_rich_text(content)

        self.assertIn('<h2>عنوان</h2>', clean)
        self.assertIn('<strong>متن</strong>', clean)
        self.assertIn('<a href="https://example.com">خوب</a>', clean)
        self.assertNotIn('javascript:', clean)
        self.assertNotIn('onclick', clean)
        self.assertNotIn('<img', clean)
        self.assertNotIn('<script', clean)

    def test_template_sanitizes_older_posts_as_well(self):
        rendered = Template('{% load rich_text %}{{ content|safe_rich_text }}').render(
            Context({'content': '<p>سلام</p><a href="data:text/html,evil">link</a>'})
        )
        self.assertIn('<p>سلام</p>', rendered)
        self.assertNotIn('data:text/html', rendered)

    def test_admin_editor_sanitizes_initial_html(self):
        widget = PostAdminForm().fields['content'].widget
        self.assertIn('admin-rich-text.js', str(widget.media))
        self.assertNotIn('onerror', widget.format_value('<img src=x onerror=alert(1)>'))


class PublicPagesTests(TestCase):
    def test_homepage_renders_agency_content(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'طراحی و توسعه وب‌سایت')
        self.assertContains(response, 'ربات تلگرام اختصاصی')
        self.assertContains(response, 'application/ld+json')

    def test_robots_is_crawlable(self):
        response = self.client.get(reverse('blog:robots'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Allow: /')
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_sitemap_is_xml(self):
        response = self.client.get(reverse('blog:sitemap'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')

# Create your tests here.
