from environs import Env
from corsheaders.defaults import default_headers

from django.conf import global_settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import django.conf.locale


from project.settings_base import *
from authentication_service.constants import LOGIN_VALIDATION_ERRORS
import access_control
import user_data_store

env = Env()

#--Project settings
HIDE_FIELDS = {
    "global_enable": True,
    "global_fields": ["email", "birth_date", "nickname", "avatar"]
}

# NOTE: If the value is not set, the celery task will error.
CLIENT_REQUEST_EMAIL = env.list("CLIENT_REQUEST_EMAIL", [])

# authentication_service/management/commands/user_login_report.py
REPORT_EMAILS = env.list("REPORT_EMAILS", [])

# Used in authentication/signals.py: Hardcoded id to be used for authentication
# service. This service can not have a client that is required to create a
# site entry.
AUTHENTICATION_SERVICE_HARDCODED_SITE_ID = 0
#--Project settings end

# Django Settings
SECRET_KEY = env.str("SECRET_KEY", "_n(_w(3!i4-p((jz8(o0fb*_r5fb5t!qh1g@m9%4vryx5lale=")

# 24hrs in seconds
SESSION_COOKIE_AGE = 86400

AUTH_USER_MODEL = "authentication_service.CoreUser"


# Defaults are for S3 and CloudFront usage
STATIC_URL = env.str("STATIC_URL", "/static/")
STATIC_ROOT = env.str("STATIC_ROOT", "/static")

MEDIA_URL = env.str("MEDIA_URL", "/media/")
MEDIA_ROOT = env.str("MEDIA_ROOT", "/media")

LOCALE_PATHS = [
    "locale"
]

LANGUAGE_CODE = "en"

# We explicitly exclude language variants.
EXCLUDED_LANGUAGE_CODES = {
    "en-au",
    "en-gb",
    "es-ar",
    "es-co",
    "es-mx",
    "es-ni",
    "es-ve",
    "pt-br",
    "sr-latn",
    "zh-hans",
    "zh-hant",
}

LANGUAGES = [
    language for language in global_settings.LANGUAGES if language[0] not in EXCLUDED_LANGUAGE_CODES
] + [
    ("tl", _("Tagalog")),
    ("rw", _("Kinyarwanda")),
    ("ha", _("Hausa")),
    ("bn", _("Bengali")),
    ("my", _("Burmese")),
    ("ny", _("Chichewa")),
    ("prs", _("Dari")),
    ("swa-tz", _("Tanzanian Swahili")),
    ("en-you", _("Springster English Youth")),
]

EXTRA_LANG_INFO = {
    "tl": {
        "bidi": False,
        "code": "tl",
        "name": "Tagalog",
        "name_local": "Tagalog"
    },
    "rw": {
        "bidi": False,
        "code": "rw",
        "name": "Kinyarwanda",
        "name_local": "Kinyarwanda"
    },
    "ha": {
        "bidi": False,
        "code": "ha",
        "name": "Hausa",
        "name_local": "Hausa"
    },
    "bn": {
        "bidi": False,
        "code": "bn",
        "name": "Bengali",
        "name_local": u"বাংলা"
    },
    "my": {
        "bidi": False,
        "code": "bur_MM",
        "name": "Burmese",
        "name_local": "Burmese"
    },
    "ny": {
        "bidi": False,
        "code": "ny",
        "name": "Chichewa",
        "name_local": "Chichewa",
    },
    "prs": {
        "bidi": False,
        "code": "prs",
        "name": "Dari",
        "name_local": u"دری",
    },
    "swa-tz": {
        "bidi": False,
        "code": "swa_TZ",
        "name": "Tanzanian Swahili",
        "name_local": "Tanzanian Swahili"
    },
}
django.conf.locale.LANG_INFO.update(EXTRA_LANG_INFO)


AUTH_PASSWORD_VALIDATORS += [
    {
        "NAME": "authentication_service.password_validation.DiversityValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "authentication_service.backends.GirlEffectAuthBackend"
]

DATABASES = {
    "default": env.dict("DB_DEFAULT",
        "ENGINE=django.db.backends.postgresql,"
        "NAME=authentication_service,"
        "USER=authentication_service,"
        "PASSWORD=password,"
        "HOST=127.0.0.1,"
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
    "celery",

    # Form helpers.
    "form_renderers",

    # CORS headers
    "corsheaders",

    # Sentry
    "raven.contrib.django.raven_compat",

    # File storage
    "storages",
]

# Project app has to be first in the list.
INSTALLED_APPS = [
    "authentication_service",
    "authentication_service.user_migration",
    "authentication_service.request_client"
] + INSTALLED_APPS + ADDITIONAL_APPS

MIDDLEWARE = [
    "authentication_service.middleware.MetricMiddleware",  # Must come first
] + MIDDLEWARE + [
    "corsheaders.middleware.CorsMiddleware",
    # Subclasses django locale.LocaleMiddleware
    "authentication_service.middleware.GELocaleMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "authentication_service.middleware.ErrorMiddleware",
    "authentication_service.middleware.SessionDataManagementMiddleware",
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
LAYERS = {
    "tree": ["base", ["springster"], ["ninyampinga"], ["chhaa-jaa"], ["zathu"]]
}

# https://docs.djangoproject.com/en/1.11/ref/settings/#password-reset-timeout-days
PASSWORD_RESET_TIMEOUT_DAYS = 3

# Defender options
DEFENDER_LOGIN_FAILURE_LIMIT = 5  # A maximum of 5 failed attempts to be allowed
DEFENDER_BEHIND_REVERSE_PROXY = False
DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = False
DEFENDER_DISABLE_IP_LOCKOUT = True
DEFENDER_DISABLE_USERNAME_LOCKOUT = False
DEFENDER_COOLOFF_TIME = 600  # seconds that failures will be remembered
DEFENDER_REVERSE_PROXY_HEADER = "HTTP_X_FORWARDED_FOR"
DEFENDER_CACHE_PREFIX = "defender"
DEFENDER_LOCKOUT_URL = "/lockout"
DEFENDER_REDIS_URL = env.str("REDIS_URI", "redis://localhost:6379/0")
DEFENDER_STORE_ACCESS_ATTEMPTS = True
DEFENDER_ACCESS_ATTEMPT_EXPIRATION = 24  # hours
DEFENDER_USERNAME_FORM_FIELD = "auth-username"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", "127.0.0.1,localhost")

# CORS settings
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST",
    "localhost:8000,127.0.0.1:8000,"  # Development: Management Layer UI
    "localhost:3000,127.0.0.1:3000,"  # Development: Management Portal
    "core-management-layer:8000,core-management-portal"  # Demo environment
)

if env.bool("USE_DEFAULT_STORAGE", True) is False:
    # CloudFront domain
    CORS_ORIGIN_WHITELIST.append(env.str("AWS_S3_CUSTOM_DOMAIN"))

CORS_ORIGIN_ALLOW_ALL = False  # Setting this to true will cause CORS_ORIGIN_WHITELIST to be ignored
CORS_ALLOW_CREDENTIALS = True  # Allow CORS requests to send cookies along
CORS_ALLOW_HEADERS = default_headers + (
    "Access-Control-Allow-Origin",
)

LOGIN_URL = reverse_lazy("login")

# To avoid the login loop, we rather redirect to a page that shows
# the message oops.
LOGIN_REDIRECT_URL = "redirect_issue"
INACTIVE_ACCOUNT_LOGIN_MESSAGE = LOGIN_VALIDATION_ERRORS['inactive']
INCORRECT_CREDENTIALS_MESSAGE = LOGIN_VALIDATION_ERRORS['invalid_login']

OIDC_USERINFO = "authentication_service.oidc_provider_settings.userinfo"
OIDC_EXTRA_SCOPE_CLAIMS = \
    "authentication_service.oidc_provider_settings.CustomScopeClaims"
OIDC_GRANT_TYPE_PASSWORD_ENABLE = True  # https://tools.ietf.org/html/rfc6749#section-4.3
OIDC_IDTOKEN_EXPIRE = 2 * 60 * 60  # Two hours
OIDC_TOKEN_EXPIRE = 2 * 60 * 60  # Two hours
OIDC_CODE_EXPIRE = 2 * 60 * 60  # Two hours

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

LOG_LEVEL = env.str("LOG_LEVEL", "info").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
                      "%(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "sentry": {
            "level": "ERROR",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
            "tags": {"custom-tag": "x"},
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        }
    },
    "loggers": {
        "": {
            "level": "WARNING",
            "handlers": ["sentry", "console"],
        },
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "raven": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry.errors": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "celery": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "authentication_service": {
            "level": LOG_LEVEL,
            "handlers": ["console", "sentry"],
            # required to avoid double logging with root logger
            "propagate": False,
        }
    },
}

RAVEN_CONFIG = {
    "dsn": env.str("SENTRY_DSN", None),
    "processors": (
        "project.processors.SanitizeHeadersProcessor",
    )
}

########################
# EXTRA SETTINGS LOGIC #
########################

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = env.str("EMAIL_USER", "")
EMAIL_HOST_PASSWORD = env.str("EMAIL_PASSWORD", "")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", None)

if not env.bool("BUILDER", False):
    # Celery workers now require the Access Control API.
    # GE API settings and setup
    ALLOWED_API_KEYS = env.list("ALLOWED_API_KEYS")
    USER_DATA_STORE_API_URL = env.str("USER_DATA_STORE_API")
    USER_DATA_STORE_API_KEY = env.str("USER_DATA_STORE_API_KEY")
    ACCESS_CONTROL_API_URL = env.str("ACCESS_CONTROL_API")
    ACCESS_CONTROL_API_KEY = env.str("ACCESS_CONTROL_API_KEY")

    # Setup API clients
    config = user_data_store.configuration.Configuration()
    config.host = USER_DATA_STORE_API_URL
    USER_DATA_STORE_API = user_data_store.api.UserDataApi(
        api_client=user_data_store.ApiClient(
            header_name="X-API-KEY",
            header_value=USER_DATA_STORE_API_KEY,
            configuration=config
        )
    )

    config = access_control.configuration.Configuration()
    config.host = ACCESS_CONTROL_API_URL
    ACCESS_CONTROL_API = access_control.api.AccessControlApi(
        api_client=access_control.ApiClient(
            header_name="X-API-KEY",
            header_value=ACCESS_CONTROL_API_KEY,
            configuration=config
        )
    )
    AC_OPERATIONAL_API = access_control.api.OperationalApi(
        api_client=access_control.ApiClient(
            header_name="X-API-KEY",
            header_value=ACCESS_CONTROL_API_KEY,
            configuration=config
        )
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

# Attempt to import local settings if present.
try:
    from project.settings_local import *
except ImportError:
    pass

# The debug flag can be overwritten by settings_local, so we check it here
# to determine whether to include
if DEBUG:
    # IPs that are considered "internal" by Django Debug Toolbar
    INTERNAL_IPS = [
        "",  # For the docker compose environment
        "127.0.0.1"  # Localhost
    ]
    INTERNAL_IPS.extend(env.list("INTERNAL_IPS", ""))  # Add additional IPs passed in the env.

    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    # remove static root from sys root on debug mode
    MEDIA_ROOT = env.str("MEDIA_ROOT", "media")
    STATIC_ROOT = env.str("STATIC_ROOT", "static")

# STORAGE
# Unless env.USE_DEFAULT_STORAGE is set to false, this service will make use of
# the default storage backend and settings.
if env.bool("USE_DEFAULT_STORAGE", True) is False:
    # Storage
    DEFAULT_FILE_STORAGE = "project.settings.FileStorage"

    # Allow collectstatic to automatically put static files in the bucket
    STATICFILES_STORAGE = "project.settings.StaticStorage"

    # CloudFront domain
    AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN")

    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")

    # Optional file paramaters
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=360",
    }
    # Create separate backends to prevent file overriding when saving to static
    # and media.
    # backends/s3boto3.py l:194; location = setting('AWS_LOCATION', '')
    from storages.backends.s3boto3 import S3Boto3Storage
    class FileStorage(S3Boto3Storage):
        location = "/"

    class StaticStorage(S3Boto3Storage):
        location = STATIC_ROOT

    class MediaStorage(S3Boto3Storage):
        """
        Media should not be on the bucket root. Means storage needs to be defined
        one each FileField.
        """
        location = MEDIA_ROOT
else:
    from django.core.files.storage import FileSystemStorage
    class MediaStorage(FileSystemStorage):
        """
        Due to MediaStorage needing to be used explicitly, it needs to be set
        for DefaultStorage as well.
        """
        location = MEDIA_ROOT
