SECURITY_QUESTION_COUNT = 2

MIN_NON_HIGH_PASSWORD_LENGTH = 4

# Dictionary key within which we should store all our extra session data. Makes
# cleanup much easier as we only need to remove one key. utils.update and get
# data methods already make use of this.
EXTRA_SESSION_KEY = "ge_session_extra_data"

SESSION_KEYS = {
    "redirect_client_uri": "ge_oidc_client_uri",
    "redirect_client_name": "ge_oidc_client_name",
    "redirect_client_terms": "ge_oidc_client_terms",
    "theme": "theme"
}

GE_TERMS_URL = "https://www.girleffect.org/terms-and-conditions/"

THEME_NAME_MAP = {
    "springster": "Springster"
}


def get_theme_client_name(request):
    theme = request.META.get("X-Django-Layer", None)
    fallback_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(SESSION_KEYS["redirect_client_name"])
    return THEME_NAME_MAP.get(theme, fallback_name)
