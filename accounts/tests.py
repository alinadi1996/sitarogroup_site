from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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

# Create your tests here.
