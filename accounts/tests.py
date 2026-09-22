from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from leads.models import ClientProject, ProjectUpdate


class AccountFlowTests(TestCase):
    def test_login_and_signup_pages_render(self):
        login_response = self.client.get(reverse('accounts:login'))
        signup_response = self.client.get(reverse('accounts:signup'))

        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, 'خوش آمدید')
        self.assertEqual(signup_response.status_code, 200)
        self.assertContains(signup_response, 'شروع همکاری')

    def test_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newclient',
            'email': 'client@example.com',
            'password1': 'SitaroStrongPass-1405',
            'password2': 'SitaroStrongPass-1405',
        })

        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(get_user_model().objects.filter(username='newclient').exists())

    def test_authenticated_homepage_shows_logout(self):
        user = get_user_model().objects.create_user(
            username='client', email='client@sitaro.test', password='SecurePass-1405'
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'حساب من')
        self.assertContains(response, 'client')
        self.assertContains(response, reverse('accounts:logout'))
        self.assertContains(response, 'mobile-auth-user')
        self.assertContains(response, 'ورود به پنل کاربری client')

    def test_mobile_navigation_has_account_action_for_guests(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'mobile-auth-login')
        self.assertContains(response, 'mobile-auth-icon')
        self.assertContains(response, 'theme-icon-sun')
        self.assertContains(response, 'theme-icon-moon')
        self.assertContains(response, reverse('accounts:login'))
        self.assertNotContains(response, 'mobile-account-panel')

    def test_profile_shows_only_the_authenticated_clients_projects_and_visible_updates(self):
        user = get_user_model().objects.create_user(username="client", email="client@example.test", password="SecurePass-1405")
        other_user = get_user_model().objects.create_user(username="other", email="other@example.test", password="SecurePass-1405")
        project = ClientProject.objects.create(client=user, title="بازطراحی سایت سیتارو", service="web_design", status=ClientProject.Status.DESIGN, progress=45)
        ProjectUpdate.objects.create(project=project, title="وایرفریم‌ها آماده شدند", message="نسخه اولیه برای بررسی آماده است.", progress=45)
        ProjectUpdate.objects.create(project=project, title="یادداشت داخلی", message="این متن نباید دیده شود.", progress=45, is_visible=False)
        ClientProject.objects.create(client=other_user, title="پروژه خصوصی دیگر", service="web_design")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بازطراحی سایت سیتارو")
        self.assertContains(response, "وایرفریم‌ها آماده شدند")
        self.assertNotContains(response, "یادداشت داخلی")
        self.assertNotContains(response, "پروژه خصوصی دیگر")

# Create your tests here.
