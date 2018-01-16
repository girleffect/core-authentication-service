from django.core.urlresolvers import reverse_lazy
from project.settings_base import *


DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("DB_NAME", "core_authentication_service"),
        "USER": os.environ.get("DB_USER", "postgres"),
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

# Only change this once custom login flow has been decided on and the need
# arises to bypass two factor for certain users.
LOGIN_URL = reverse_lazy("login")

LOGIN_REDIRECT_URL = "admin:index"
