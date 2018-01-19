from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, resolve_url
from django.utils.http import is_safe_url

from two_factor import signals
from two_factor.views import core


class LoginView(core.LoginView):
    """This view simply extends the LoginView from two_factor.views.core. We
    only override the template and the done step, which we use to login
    superusers.
    """

    template_name = "core-authentication-service/login.html"

    def done(self, form_list, **kwargs):
        if self.get_user().is_superuser:
            login(self.request, self.get_user())

        redirect_to = self.request.POST.get(
            "next",
            self.request.GET.get("next", '')
        )
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        device = getattr(self.get_user(), 'otp_device', None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request,
                                       user=self.get_user(), device=device)
        return redirect(redirect_to)
