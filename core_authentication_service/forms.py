from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "birth_date", "country", "avatar"
        ]

    def __init__(self, security=None, *args, **kwargs):
        self.security = security
        # TODO Remove help text if not high security.
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        # Short circuit normal validation if not high security.
        if self.security == "high":
            return super(RegistrationForm, self).clean_password2()

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        if not len(password1) > 4 and not len(password2) > 4:
            raise forms.ValidationError(
                "Password not long enough."
            )
        return password2

    def clean(self):
        email = self.cleaned_data.get("email")
        msisdn = self.cleaned_data.get("msisdn")

        if not email and not msisdn:
            raise ValidationError("Enter either email or msisdn")

        return super(RegistrationForm, self).clean()
