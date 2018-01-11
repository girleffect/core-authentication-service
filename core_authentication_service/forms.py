from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from core_authentication_service.utils import update_form_fields

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
        if self.security == "high":
            update_form_fields(self, required=["email"])
        else:
            data = {
                "password1": {
                    "attributes": {
                        "help_text": ""
                    }
                }
            }
            update_form_fields(self, fields_data=data)

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

        # NOTE: Min length might need to be defined somewhere easier to change.
        # Setting doesn't feel 100% right though.
        if not len(password1) > 3 and not len(password2) > 3:
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
