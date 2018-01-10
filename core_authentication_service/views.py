from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class RegistrationView(CreateView):
    template_name = "core_authentication_service/registration.html"
    model = get_user_model()
    form_class = UserCreationForm
    success_url = "/"
