from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from core_authentication_service import forms


class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = "core-authentication-service/login.html"

    def get_success_url(self):
        return reverse(self.request.GET.get("next"))
