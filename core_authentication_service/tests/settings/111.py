from django.core.urlresolvers import reverse_lazy
from project.settings_base import *


SECRET_KEY = os.environ.get("SECRET_KEY", "_n(_w(3!i4-p((jz8(o0fb*_r5fb5t!qh1g@m9%4vryx5lale=")

AUTH_USER_MODEL = "core_authentication_service.CoreUser"

AUTH_PASSWORD_VALIDATORS = AUTH_PASSWORD_VALIDATORS + [
    {
        "NAME": "core_authentication_service.password_validation.DiversityValidator",
    },
]

# NOTE missing password, host and port for passwordless connection.
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("DB_NAME", "core_authentication_service"),
        "USER": os.environ.get("DB_USER", "postgres"),
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

    # Form helpers.
    "form_renderers",
]

# Project app has to be first in the list.
INSTALLED_APPS = ["core_authentication_service"] + INSTALLED_APPS + ADDITIONAL_APPS

MIDDLEWARE = MIDDLEWARE + [
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware"
]

# Only change this once custom login flow has been decided on and the need
# arises to bypass two factor for certain users.
LOGIN_URL = reverse_lazy("two_factor_auth:login")

OIDC_USERINFO = "core_authentication_service.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = \
    "core_authentication_service.oidc_provider_settings.CustomScopeClaims"

FORM_RENDERERS = {"replace-as-p": True, "replace-as-table": True}
FORM_RENDERERS = {"enable-bem-classes": True}
