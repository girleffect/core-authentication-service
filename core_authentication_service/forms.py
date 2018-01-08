from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

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
