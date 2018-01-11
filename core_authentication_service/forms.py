from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisd", "birth_date", "country", "avatar"
        ]
