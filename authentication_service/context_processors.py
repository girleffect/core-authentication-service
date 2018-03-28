from django.conf import settings

from authentication_service.constants import COOKIES, EXTRA_SESSION_KEY

def global_context(request):
    session_client_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(COOKIES["redirect_client_name"])
    return {
        "ge_global_redirect_uri": request.COOKIES.get(
            COOKIES["redirect_cookie"]
        ),
        "ge_global_client_name": request.COOKIES.get(
            COOKIES["redirect_client_name"], session_client_name
        )
    }
