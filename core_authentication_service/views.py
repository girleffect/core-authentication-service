from django.contrib.auth import login
from django.shortcuts import resolve_url, redirect
from django.utils.http import is_safe_url
from django_otp.plugins.otp_static.models import StaticDevice
from two_factor import signals

from two_factor.utils import default_device
from two_factor.views.utils import IdempotentSessionWizardView
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm

from core_authentication_service import forms


class LoginView(IdempotentSessionWizardView):
    """This view handles the login process. The first step asks for the user's
    username and password. If the username and password is correct, it will
    check if the user has 2FA enabled. If enabled, the second step is displayed
    that requires the user to enter a OTP generated by a device (phone in this
    case).

    An IdempotentSessionWizard is used for this allowing certain steps to be
    marked non-idempotent, in which case the form is only validated once and the
    cleaned values stored.

    Adapted from two_factor.views.core"""
    template_name = "core-authentication-service/login.html"
    form_list = (
        ("credentials", forms.LoginForm),
        ("token", AuthenticationTokenForm),
        ("backup", BackupTokenForm),
    )

    idempotent_dict = {
        "token": False,
        "backup": False,
    }

    def has_token_step(self):
        return default_device(self.get_user())

    def has_backup_step(self):
        return default_device(self.get_user()) and \
               "token" not in self.storage.validated_step_data

    condition_dict = {
        "token": has_token_step,
        "backup": has_backup_step,
    }

    def __init__(self, **kwargs):
        super(LoginView, self).__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None

    def done(self, form_list, **kwargs):
        """Log user in and direct them back to the site they came from."""
        login(self.request, self.get_user())

        redirect_to = self.request.POST.get(
            "next",
            self.request.GET.get("next", '')
        )
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url("back to where you came from")

        device = getattr(self.get_user(), 'otp_device', None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request,
                                       user=self.get_user(), device=device)
        return redirect(redirect_to)

    def get_form_kwargs(self, step=None):
        if step == "credentials":
            return {
                "request": self.request
            }
        if step in ("token", "backup"):
            return {
                "user": self.get_user(),
                "initial_device": self.get_device(step)
            }
        return {}

    def get_device(self, step=None):
        if not self.device_cache:
            self.device_cache = default_device(self.get_user())
        if step == "backup":
            try:
                self.device_cache = self.get_user().staticdevice_set.get(
                    name="backup")
            except StaticDevice.DoesNotExist:
                pass
        return self.device_cache

    def get_user(self):
        """Return the authenticated user or None if user isn't authenticated."""
        if not self.user_cache:
            form_obj = self.get_form(
                step="credentials",
                data=self.storage.get_step_data("credentials")
            )
            self.user_cache = form_obj.is_valid() and form_obj.user_cache
        return self.user_cache

    def get_context_data(self, form, **kwargs):
        context = super(LoginView, self).get_context_data(form, **kwargs)
        if self.steps.current == "token":
            context["device"] = self.get_device()
            try:
                context["backup_tokens"] = self.get_user().staticdevice_set.get(
                    name="backup").token_set.count()
            except StaticDevice.DoesNotExist:
                context["backup_tokens"] = 0
        return context
