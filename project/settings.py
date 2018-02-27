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

AUTHENTICATION_BACKENDS = \
    ["authentication_service.backends.GirlEffectAuthBackend"]

# https://docs.djangoproject.com/en/1.11/ref/settings/#password-reset-timeout-days
PASSWORD_RESET_TIMEOUT_DAYS = 3

# Defender options
DEFENDER_LOGIN_FAILURE_LIMIT = 5
DEFENDER_BEHIND_REVERSE_PROXY = False
DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = True
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_DISABLE_USERNAME_LOCKOUT = False
DEFENDER_COOLOFF_TIME = 600  # seconds
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
        "USER": os.environ.get("DB_USER", "authentication_service"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# CORS settings
CORS_ORIGIN_WHITELIST = ["localhost:8000", "127.0.0.1:8000"]
CORS_ORIGIN_ALLOW_ALL = False  # Setting this to true will cause CORS_ORIGIN_WHITELIST to be ignored


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

    # CORS headers
    "corsheaders",
]

# Project app has to be first in the list.
INSTALLED_APPS = ["authentication_service"] + INSTALLED_APPS + ADDITIONAL_APPS

MIDDLEWARE = MIDDLEWARE + [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "authentication_service.middleware.ThemeManagementMiddleware",
    "authentication_service.middleware.OIDCSessionManagementMiddleware",
]

LOGIN_URL = reverse_lazy("login")

# To avoid the login loop, we rather redirect to a page that shows
# the message oops.
LOGIN_REDIRECT_URL = "oops"

OIDC_USERINFO = "authentication_service.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = \
    "authentication_service.oidc_provider_settings.CustomScopeClaims"

FORM_RENDERERS = {
    "replace-as-p": True,
    "replace-as-table": True,
    "enable-bem-classes": True
}

CELERY_USE_TZ = USE_TZ
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://myuser:mypassword@localhost:5672//")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Attempt to import local settings if present.
try:
    from project.settings_local import *
except ImportError:
    pass
