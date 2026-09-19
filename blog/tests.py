from django.test import TestCase
from django.urls import reverse


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
