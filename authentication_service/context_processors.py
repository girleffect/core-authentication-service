from django.conf import settings

from authentication_service.constants import (
    COOKIES, EXTRA_SESSION_KEY, GE_TERMS_URL, get_theme_client_name
)

def global_context(request):
    session_client_name = get_theme_client_name(request)
    session_client_terms = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(COOKIES["redirect_client_terms"], GE_TERMS_URL)
    return {
        "ge_global_redirect_uri": request.COOKIES.get(
            COOKIES["redirect_cookie"]
        ),
        "ge_global_client_name": request.COOKIES.get(
            COOKIES["redirect_client_name"], session_client_name
        ),
        "ge_global_client_terms": request.COOKIES.get(
            COOKIES["redirect_client_terms"], session_client_terms
        )
    }
