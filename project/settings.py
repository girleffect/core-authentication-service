from environs import Env
from corsheaders.defaults import default_headers

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from project.settings_base import *

env = Env()

# Project Settings
HIDE_FIELDS = {
    "global_enable": True,
    "global_fields": ["email", "msisdn", "birth_date"]
}

# Django Settings
SECRET_KEY = env.str("SECRET_KEY", "_n(_w(3!i4-p((jz8(o0fb*_r5fb5t!qh1g@m9%4vryx5lale=")

# 24hrs in seconds
SESSION_COOKIE_AGE = 86400

AUTH_USER_MODEL = "authentication_service.CoreUser"

STATIC_URL = "/static/"
STATIC_ROOT = "/static/"

LOCALE_PATHS = [
    "locale"
]

LANGUAGE_CODE = "en"

AUTH_PASSWORD_VALIDATORS += [
    {
        "NAME": "authentication_service.password_validation.DiversityValidator",
    },
]

AUTHENTICATION_BACKENDS = \
    ["authentication_service.backends.GirlEffectAuthBackend"]

DATABASES = {
    "default": env.dict("DB_DEFAULT", "ENGINE=django.db.backends.postgresql," \
        "NAME=authentication_service," \
        "USER=authentication_service," \
        "PASSWORD=password," \
        "HOST=127.0.0.1," \
        "PORT=5432")
}

INSTALLED_APPS = list(INSTALLED_APPS)

ADDITIONAL_APPS = [
    "layers",
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
    "django_otp.middleware.OTPMiddleware",
    "authentication_service.middleware.ThemeManagementMiddleware",
    "authentication_service.middleware.OIDCSessionManagementMiddleware",
    "authentication_service.middleware.RedirectManagementMiddleware",
    "crum.CurrentRequestUserMiddleware",
]

# TODO: django-layers-hr needs looking into
# Request based layering has an issue due to the crum package setting current
# request to None before static is requested.
#STATICFILES_FINDERS = (
#    "layers.finders.FileSystemFinder",
#    "django.contrib.staticfiles.finders.FileSystemFinder",
#    "layers.finders.AppDirectoriesFinder",
#    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
#)

# django-layers-hr
LAYERS = {"tree": ["base", ["springster"], ["ninyampinga"]]}

# https://docs.djangoproject.com/en/1.11/ref/settings/#password-reset-timeout-days
PASSWORD_RESET_TIMEOUT_DAYS = 3

# Defender options
DEFENDER_LOGIN_FAILURE_LIMIT = 5
DEFENDER_BEHIND_REVERSE_PROXY = False
DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = True
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_DISABLE_USERNAME_LOCKOUT = False
DEFENDER_COOLOFF_TIME = 600  # seconds
DEFENDER_REVERSE_PROXY_HEADER = "HTTP_X_FORWARDED_FOR"
DEFENDER_CACHE_PREFIX = "defender"
DEFENDER_LOCKOUT_URL = "/lockout"
DEFENDER_REDIS_URL = env.str("REDIS_URI", "redis://localhost:6379/0")
DEFENDER_STORE_ACCESS_ATTEMPTS = True
DEFENDER_ACCESS_ATTEMPT_EXPIRATION = 24  # hours
DEFENDER_USERNAME_FORM_FIELD = "auth-username"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_API_KEYS = env.list("ALLOWED_API_KEYS")
USER_DATA_STORE_API = env.str("USER_DATA_API")
USER_DATA_STORE_API_KEY = env.str("USER_DATA_STORE_API_KEY")
ACCESS_CONTROL_API = env.str("ACCESS_CONTROL_API")
ACCESS_CONTROL_API_KEY = env.str("ACCESS_CONTROL_API_KEY")

# CORS settings
CORS_ORIGIN_WHITELIST = [
    "localhost:8000", "127.0.0.1:8000",  # Development: Management Layer UI
    "localhost:3000", "127.0.0.1:3000",  # Development: Management Portal
    "core-management-layer:8000", "core-management-portal:3000",  # Demo environment
]
CORS_ORIGIN_ALLOW_ALL = False  # Setting this to true will cause CORS_ORIGIN_WHITELIST to be ignored
CORS_ALLOW_HEADERS = default_headers + (
    "Access-Control-Allow-Origin",
)


LOGIN_URL = reverse_lazy("login")

# To avoid the login loop, we rather redirect to a page that shows
# the message oops.
LOGIN_REDIRECT_URL = "redirect_issue"

OIDC_USERINFO = "authentication_service.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = \
    "authentication_service.oidc_provider_settings.CustomScopeClaims"
OIDC_GRANT_TYPE_PASSWORD_ENABLE = True  # https://tools.ietf.org/html/rfc6749#section-4.3
OIDC_IDTOKEN_EXPIRE = 60 * 60  # An hour

FORM_RENDERERS = {
    "replace-as-p": True,
    "replace-as-table": True,
    "enable-bem-classes": True
}

# Celery Settings
CELERY_USE_TZ = USE_TZ
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# API Settings
STUBS_CLASS = "authentication_service.integration.Implementation"
SWAGGER_API_VALIDATE_RESPONSES = True
DEFAULT_LISTING_LIMIT = 20
MAX_LISTING_LIMIT = 100
MIN_LISTING_LIMIT = 1
DEFAULT_LISTING_OFFSET = 0


# Attempt to import local settings if present.
try:
    from project.settings_local import *
except ImportError:
    pass
