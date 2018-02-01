import os
from django.core.urlresolvers import reverse_lazy
from project.settings_base import *


SECRET_KEY = os.environ.get("SECRET_KEY", "_n(_w(3!i4-p((jz8(o0fb*_r5fb5t!qh1g@m9%4vryx5lale=")

AUTH_USER_MODEL = "authentication_service.CoreUser"

AUTH_PASSWORD_VALIDATORS += [
    {
        "NAME": "authentication_service.password_validation.DiversityValidator",
    },
]

# Defender options
DEFENDER_LOGIN_FAILURE_LIMIT = 3
DEFENDER_BEHIND_REVERSE_PROXY = False
DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = True
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_DISABLE_USERNAME_LOCKOUT = False
DEFENDER_COOLOFF_TIME = 300  # seconds
DEFENDER_LOCKOUT_TEMPLATE = "authentication_service/lockout.html"
DEFENDER_REVERSE_PROXY_HEADER = "HTTP_X_FORWARDED_FOR"
DEFENDER_CACHE_PREFIX = "defender"
DEFENDER_LOCKOUT_URL = "/lockout"
DEFENDER_REDIS_URL = os.environ.get("REDIS_URI", "redis://localhost:6379/0")
DEFENDER_STORE_ACCESS_ATTEMPTS = True
DEFENDER_ACCESS_ATTEMPT_EXPIRATION = 24  # hours
DEFENDER_USERNAME_FORM_FIELD = "auth-username"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("DB_NAME", "authentication_service"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS")]


ADDITIONAL_APPS = [
    # Open ID prodiver.
    "oidc_provider",

    # Two factor auth apps.
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
    "defender",

    # Form helpers.
    "form_renderers",
]

# Project app has to be first in the list.
INSTALLED_APPS = ["authentication_service"] + INSTALLED_APPS + ADDITIONAL_APPS

MIDDLEWARE = MIDDLEWARE + [
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
]

# Only change this once custom login flow has been decided on and the need
# arises to bypass two factor for certain users.
LOGIN_URL = reverse_lazy("login")

LOGIN_REDIRECT_URL = "admin:index"

OIDC_USERINFO = "authentication_service.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = \
    "authentication_service.oidc_provider_settings.CustomScopeClaims"

FORM_RENDERERS = {
    "replace-as-p": True,
    "replace-as-table": True,
    "enable-bem-classes": True
}

# Attempt to import local settings if present.
try:
    from project.settings_local import *
except ImportError:
    pass
