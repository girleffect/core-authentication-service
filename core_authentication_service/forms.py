from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            raise ValidationError(_("Please enter you username."))
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise ValidationError(_("Please enter your password."))
        return password

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if User.objects.filter(username=username).exists():
            self.user_cache = authenticate(
                self.request, username=username, password=password)
        else:
            raise forms.ValidationError(
                _("Login failed. Please try again.")
            )
        return self.cleaned_data
