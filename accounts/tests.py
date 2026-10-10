import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from leads.models import ClientProject, ProjectStrategy, ProjectUpdate, SEOKeyword


class AccountFlowTests(TestCase):
    def test_login_and_signup_pages_render(self):
        login_response = self.client.get(reverse('account_login'))
        signup_response = self.client.get(reverse('account_signup'))

        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, 'خوش آمدید')
        self.assertEqual(signup_response.status_code, 200)
        self.assertContains(signup_response, 'شروع همکاری')

    def test_signup_creates_user_and_redirects_home(self):
        response = self.client.post(reverse('account_signup'), {
            'username': 'newclient',
            'email': 'client@example.com',
            'password1': 'SitaroStrongPass-1405',
            'password2': 'SitaroStrongPass-1405',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(get_user_model().objects.filter(username='newclient').exists())

    def test_authenticated_homepage_shows_logout(self):
        user = get_user_model().objects.create_user(
            username='client', email='client@sitaro.test', password='SecurePass-1405'
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'حساب من')
        self.assertContains(response, 'client')
        self.assertContains(response, reverse('account_logout'))
        self.assertContains(response, 'mobile-auth-user')
        self.assertContains(response, 'منوی حساب کاربری client')
        self.assertContains(response, 'data-mobile-account-panel')
        self.assertContains(response, reverse('accounts:profile_edit'))
        self.assertContains(response, reverse('account_change_password'))

    def test_mobile_navigation_has_account_action_for_guests(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'mobile-auth-login')
        self.assertContains(response, 'mobile-auth-icon')
        self.assertContains(response, 'theme-icon-sun')
        self.assertContains(response, 'theme-icon-moon')
        self.assertContains(response, reverse('account_login'))
        self.assertNotContains(response, 'mobile-account-panel')

    def test_profile_edit_requires_login_and_updates_only_current_user(self):
        url = reverse('accounts:profile_edit')
        self.assertEqual(self.client.get(url).status_code, 302)
        user = get_user_model().objects.create_user(
            username='client', email='client@example.test', password='SecurePass-1405'
        )
        other = get_user_model().objects.create_user(
            username='other', email='other@example.test', password='SecurePass-1405'
        )
        self.client.force_login(user)
        self.assertContains(self.client.get(url), 'ویرایش پروفایل')
        response = self.client.post(url, {
            'first_name': 'آرمان', 'last_name': 'احمدی', 'username': 'client-updated',
        })

        self.assertRedirects(response, reverse('accounts:profile'))
        user.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(user.first_name, 'آرمان')
        self.assertEqual(user.username, 'client-updated')
        self.assertEqual(other.username, 'other')
        self.assertEqual(user.email, 'client@example.test')

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

    def test_profile_shows_visible_strategy_and_seo_keywords_only(self):
        user = get_user_model().objects.create_user(username="seo-client", email="seo@example.test", password="SecurePass-1405")
        project = ClientProject.objects.create(client=user, title="رشد ارگانیک", service="seo_performance")
        ProjectStrategy.objects.create(project=project, summary="تمرکز بر صفحات خدمات و محتوای هدفمند.", current_focus="تحقیق خوشه‌های محتوایی", next_step="تهیه تقویم محتوا")
        SEOKeyword.objects.create(project=project, keyword="طراحی سایت شرکتی", priority=SEOKeyword.Priority.PRIMARY, status=SEOKeyword.Status.OPTIMIZING, current_position=12)
        SEOKeyword.objects.create(project=project, keyword="کلمه داخلی", is_visible=False)
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertContains(response, "تمرکز بر صفحات خدمات")
        self.assertContains(response, "طراحی سایت شرکتی")
        self.assertContains(response, "رتبه 12")
        self.assertNotContains(response, "کلمه داخلی")


class PasswordPageTests(TestCase):
    def test_password_change_renders_fields_and_changes_password(self):
        user = get_user_model().objects.create_user(
            username='password-client', email='password@example.test', password='OriginalPass-1405'
        )
        self.client.force_login(user)
        url = reverse('account_change_password')

        response = self.client.get(url)
        self.assertContains(response, 'name="oldpassword"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

        response = self.client.post(url, {
            'oldpassword': 'OriginalPass-1405',
            'password1': 'UpdatedSecurePass-1405',
            'password2': 'UpdatedSecurePass-1405',
        }, follow=True)
        user.refresh_from_db()
        self.assertTrue(user.check_password('UpdatedSecurePass-1405'))
        self.assertContains(response, 'تغییر رمز عبور')

    def test_reset_pages_render_the_email_and_new_password_forms(self):
        response = self.client.get(reverse('account_reset_password'))
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'ارسال لینک بازیابی')

        response = self.client.get(reverse('account_reset_password_from_key', args=['invalid', 'invalid']))
        self.assertContains(response, 'این لینک دیگر معتبر نیست')
        self.assertContains(response, reverse('account_reset_password'))

    @override_settings(MAILERS={'default': {'BACKEND': 'django.core.mail.backends.locmem.EmailBackend'}})
    def test_reset_link_accepts_new_password(self):
        user = get_user_model().objects.create_user(
            username='reset-client', email='reset@example.test', password='OriginalPass-1405'
        )
        response = self.client.post(reverse('account_reset_password'), {'email': user.email})
        self.assertRedirects(response, reverse('account_reset_password_done'))
        self.assertEqual(len(mail.outbox), 1)
        reset_url = re.search(r'https?://[^\s]+/accounts/password/reset/key/[^\s]+', mail.outbox[0].body).group()

        response = self.client.get(reset_url, follow=True)
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        response = self.client.post(response.request['PATH_INFO'], {
            'password1': 'ResetSecurePass-1405',
            'password2': 'ResetSecurePass-1405',
        }, follow=True)
        self.assertContains(response, 'دسترسی شما')
        user.refresh_from_db()
        self.assertTrue(user.check_password('ResetSecurePass-1405'))

# Create your tests here.
