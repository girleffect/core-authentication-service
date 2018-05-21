from django.conf import settings

from authentication_service.constants import (
    COOKIES, EXTRA_SESSION_KEY, GE_TERMS_URL, get_theme_client_name
)
from authentication_service import utils

def global_context(request):
    session_client_name = get_theme_client_name(request)
    session_client_name = utils.get_session_data(
        request, COOKIES["redirect_client_name"]
    )
    session_client_terms = utils.get_session_data(
        request,
        COOKIES["redirect_client_terms"]
    )
    return {
        "ge_global_redirect_uri": utils.get_session_data(
            request, COOKIES["redirect_cookie"]
        ),
        "ge_global_client_name":  session_client_name,
        "ge_global_client_terms": session_client_terms or GE_TERMS_URL
    }
