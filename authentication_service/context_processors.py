from django.conf import settings

import logging

from authentication_service.constants import (
    SessionKeys, EXTRA_SESSION_KEY, GE_TERMS_URL, get_theme_client_name
)
from authentication_service import utils

LOGGER = logging.getLogger(__name__)

def global_context(request):
    session_client_name = get_theme_client_name(request)
    session_client_terms = utils.get_session_data(
        request,
        SessionKeys.CLIENT_TERMS
    )
    return {
        "ge_global_redirect_uri": utils.get_session_data(
            request, SessionKeys.CLIENT_URI
        ),
        "ge_global_client_name":  session_client_name,
        "ge_global_client_terms": session_client_terms or GE_TERMS_URL,
        # Convenience value
        "ge_global_theme": request.META.get("X-Django-Layer", None)
    }
