from urllib.parse import urlparse, parse_qs
import logging
import os

from oidc_provider.lib.endpoints.authorize import AuthorizeEndpoint
from oidc_provider.lib.errors import (
    AuthorizeError,
    ClientIdError,
    RedirectUriError
)


from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from authentication_service.constants import COOKIES, EXTRA_SESSION_KEY


LOGGER = logging.getLogger(__name__)


class OIDCSessionManagementMiddleware(MiddlewareMixin):
    """
    Middleware to ensure the user session is flushed when the user is
    directed off domain. At this stage only OIDC redirects off domain.

    This is to guard against users logging out of a client site, but their
    session still being retained on the auth service. This leads to the
    previous user being immediately logged in without a login prompt.

    NOTE: This Middleware should always be as near the end of the Middleware
    list in settings. Middleware is evaluated in order and this needs to happen
    as near the end as possible. As other Middleware may also trigger
    redirects.
    """
    # TODO Refactor cookie code, keys need to be constants or setting. Clear
    # all cookies in the flush logic.
    def process_response(self, request, response):
        if response.status_code == 302:
            current_host = request.get_host()
            location = response.get("Location", "")
            parsed_url = urlparse(location)
            if parsed_url.netloc != "" and current_host != parsed_url.netloc:
                request.session.flush()
                LOGGER.warning(
                    "User redirected off domain; " \
                    "(%s) -> (%s). Session flushed." % (
                        current_host, parsed_url.netloc
                    )
                )

                # Clear theme cookie
                response.delete_cookie(COOKIES["ge_theme_middleware_cookie"])

        return response

def fetch_theme(request, key=None):
    theme = request.GET.get("theme", None) or request.COOKIES.get(key)

    # Next querystring contain the entire url and querystrings. Django is
    # not aware of the inner querystrings.
    next_query = request.GET.get("next")
    if next_query and "theme" in next_query:
        theme = theme or parse_qs(
            urlparse(next_query).query
        ).get("theme", [None])[0]
    return theme


class ThemeManagementMiddleware(MiddlewareMixin):
    cookie_key = COOKIES["ge_theme_middleware_cookie"]

    def process_request(self, request):
        theme = fetch_theme(request, self.cookie_key)
        request.META["X-Django-Layer"] = theme

    def process_template_response(self, request, response):
        theme = fetch_theme(request, self.cookie_key)
        if theme:
            response.set_cookie(
                self.cookie_key, value=theme, httponly=True
            )
        return response


class RedirectManagementMiddleware(MiddlewareMixin):
    cookie_key = COOKIES["redirect_cookie"]
    client_name_key = COOKIES["redirect_client_name"]
    oidc_values = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Before storing the redirect_uri, ensure it comes from a valid client.
        # This is to prevent urls on other parts of the site being misused to
        # redirect users to none client apps.
        uri = request.GET.get("redirect_uri", None)
        if uri and request.method != "POST":
            authorize = AuthorizeEndpoint(request)
            try:
                authorize.validate_params()
            except (ClientIdError, RedirectUriError) as e:
                return render(
                    request,
                    "authentication_service/redirect_middleware_error.html",
                    {"error": e.error, "message": e.description, "uri": uri},
                    status=500
                )
            except AuthorizeError as e:
                # Suppress one of the errors oidc raises. It is not required
                # for pages beyond login.
                if e.error == "unsupported_response_type":
                    pass
                else:
                    raise e
            self.oidc_values = authorize
            request.session[EXTRA_SESSION_KEY] = {
                self.client_name_key: authorize.client.name
            }

    def process_response(self, request, response):
        if self.oidc_values:
            response.set_cookie(
                self.cookie_key, value=self.oidc_values.params["redirect_uri"],
                httponly=True
            )

            # Explicitly set a second cookie, less refactoring needed in other
            # parts of auth service.
            response.set_cookie(
                self.client_name_key, value=self.oidc_values.client.name,
                httponly=True
            )
        return response
