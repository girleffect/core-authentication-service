from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.utils import six
from django.utils.translation import ugettext as _

# Lifted from Django user model validator.
USERNAME_VALIDATOR = (UnicodeUsernameValidator()
    if six.PY3 else ASCIIUsernameValidator()
)


class UserDataForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[USERNAME_VALIDATOR],
    )
    age = forms.IntegerField(
        min_value=1,
        max_value=100
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if get_user_model().objects.filter(username=username).count() > 0:
            raise forms.ValidationError(
                _("A user with that username already exists.")
            )
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        if len(password2) < 4:
            raise forms.ValidationError(
                _("Password needs to be at least 4 characters long.")
            )
        return password2
