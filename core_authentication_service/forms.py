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

    def clean(self):
        email = self.cleaned_data.get("email")
        msisdn = self.cleaned_data.get("msisdn")

        if not email and not msisdn:
            raise ValidationError("Enter either email or msisdn")

        return super(RegistrationForm, self).clean()
