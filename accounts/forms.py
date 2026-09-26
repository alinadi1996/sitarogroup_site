from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django import forms

from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': 'دو رمز عبور با یکدیگر یکسان نیستند.',
    }

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'username',  )
        labels = {'username': 'نام کاربری', 'email': 'ایمیل'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'password1': 'رمز عبور',
            'password2': 'تکرار رمز عبور',
        }
        for name, field in self.fields.items():
            field.label = labels.get(name, field.label)
            autocomplete = 'email' if name == 'email' else name
            field.widget.attrs.update({'class': 'auth-input', 'autocomplete': autocomplete})
        self.fields['username'].help_text = 'فقط حروف، اعداد و نشانه‌های @ . + - _ مجاز است.'
        self.fields['password1'].help_text = 'حداقل ۸ کاراکتر و متفاوت از اطلاعات شخصی شما.'
        self.fields['password2'].help_text = 'رمز عبور را برای اطمینان دوباره وارد کنید.'


class PersianAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['password'].label = 'رمز عبور'
        self.fields['username'].widget.attrs.update({
            'class': 'auth-input', 'autocomplete': 'username', 'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': 'auth-input', 'autocomplete': 'current-password',
        })




class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username')
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'username': 'نام کاربری',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'auth-input', 'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'class': 'auth-input', 'autocomplete': 'family-name'}),
            'username': forms.TextInput(attrs={'class': 'auth-input', 'autocomplete': 'username'}),
        }
