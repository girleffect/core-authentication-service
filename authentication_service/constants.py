# Dictionary key within which we should store all our extra session data. Makes
# cleanup much easier as we only need to remove one key. utils.update and get
# data methods already make use of this.
EXTRA_SESSION_KEY = "ge_session_extra_data"


class SessionKeys:
    CLIENT_URI = "ge_oidc_client_uri"
    CLIENT_NAME = "ge_oidc_client_name"
    CLIENT_TERMS = "ge_oidc_client_terms"
    CLIENT_ID = "ge_client_django_id"
    THEME = "theme"

SECURITY_QUESTION_COUNT = 2

MIN_NON_HIGH_PASSWORD_LENGTH = 4

GE_TERMS_URL = "https://www.girleffect.org/terms-and-conditions/"

THEME_NAME_MAP = {
    "springster": "Springster"
}


def get_theme_client_name(request):
    theme = request.META.get("X-Django-Layer", None)
    fallback_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(SessionKeys.CLIENT_NAME)
    return THEME_NAME_MAP.get(theme, fallback_name)
