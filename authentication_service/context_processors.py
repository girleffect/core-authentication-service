from django.conf import settings

from authentication_service.constants import COOKIES, EXTRA_SESSION_KEY

def global_context(request):
    session_client_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(COOKIES["redirect_client_name"])

    # As we can not do template side if statements in the static tags, we need
    # to setup the static url paths here.
    theme =  request.COOKIES.get(COOKIES["ge_theme_middleware_cookie"], None)
    base = settings.STATIC_URL
    css_path = "authentication_service/css/"
    themes = {
        "basic": f"{base}{css_path}style.basic.css",
        "enhanced": f"{base}{css_path}style.enhanced.css",
    }

    # TODO: We need an elegant fallback like the template solution.
    if theme:
        themes["basic"] = f"{base}{css_path}theme/{theme}.basic.css"
        themes["enhanced"] = f"{base}{css_path}theme/{theme}.enhanced.css"
    return {
        "ge_global_redirect_uri": request.COOKIES.get(
            COOKIES["redirect_cookie"]
        ),
        "ge_global_client_name": request.COOKIES.get(
            COOKIES["redirect_client_name"], session_client_name
        ),
        "ge_global_theme": themes
    }
