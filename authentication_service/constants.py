SECURITY_QUESTION_COUNT = 2

MIN_NON_HIGH_PASSWORD_LENGTH = 4

EXTRA_SESSION_KEY = "ge_session_extra_data"

SESSION_KEYS = {
    "redirect_cookie": "ge_redirect_cookie",
    "redirect_client_name": "ge_oidc_client_name",
    "redirect_client_terms": "ge_oidc_client_terms",
    "ge_theme_middleware_cookie": "ge_theme_middleware_cookie"
}

GE_TERMS_URL = "https://www.girleffect.org/terms-and-conditions/"

THEME_NAME_MAP = {
    "springster": "Springster"
}

def get_theme_client_name(request):
    theme = request.META["X-Django-Layer"]
    fallback_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(SESSION_KEYS["redirect_client_name"])
    return THEME_NAME_MAP.get(theme, fallback_name)
