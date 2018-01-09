from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings

from core_authentication_service import forms


class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = "core-authentication-service/login.html"

    def form_valid(self, form):
        # If attempts does not exist, set to 0
        if "attempts" not in self.request.session:
            self.request.session["attempts"] = 0
        self.request.session["attempts"] = self.request.session["attempts"] + 1

        if self.request.session["attempts"] > settings.MAX_ATTEMPTS:
            self.request.session["last_attempt"] = now().timestamp()
            form.add_error(None, ValueError(
                _("Too many failed attempts. Please try again later.")))
            return super(LoginView, self).form_invalid(form)

        if form.is_valid():
            username = form.cleaned_data["username"]
            # Form is invalid if the user does not exist. Skip the rest of the
            # checks and return to the form again.
            exists = User.objects.filter(username=username).exists()
            if not exists:
                self.request.session["last_attempt"] = now().timestamp()
                form.add_error(None, ValueError(
                    _("Login failed. Please try again")))
                return super(LoginView, self).form_invalid(form)

            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user:
                login(self.request, user)
                return super(LoginView, self).form_valid(form)
            else:
                form.add_error(None, ValueError(
                    _("Login failed. Please try again")))
                return super(LoginView, self).form_invalid(form)

    def get_success_url(self):
        return reverse(self.request.GET.get("next"))
