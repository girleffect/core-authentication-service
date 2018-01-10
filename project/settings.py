from django.core.urlresolvers import reverse_lazy
from project.settings_base import *


SECRET_KEY = os.environ.get("SECRET_KEY", "_n(_w(3!i4-p((jz8(o0fb*_r5fb5t!qh1g@m9%4vryx5lale=")

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("DB_NAME", "core_authentication_service"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)

ADDITIONAL_APPS = [
    # Open ID prodiver.
    "oidc_provider",

    # Two factor auth apps.
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
]

# Project app has to be first in the list.
INSTALLED_APPS = ["core_authentication_service"] + INSTALLED_APPS + ADDITIONAL_APPS

MIDDLEWARE += ["django_otp.middleware.OTPMiddleware"]

# Only change this once custom login flow has been decided on and the need
# arises to bypass two factor for certain users.
LOGIN_URL = reverse_lazy("two_factor_auth:login")

OIDC_EXTRA_SCOPE_CLAIMS = \
    "core_authentication_service.oidc_provider_settings.CustomScopeClaims"
