import copy
from urllib.parse import urlparse, parse_qs
import logging

from django.urls import reverse
from oidc_provider.lib.endpoints.authorize import AuthorizeEndpoint
from oidc_provider.lib.errors import (
    AuthorizeError,
    ClientIdError,
    RedirectUriError
)


from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseBadRequest, HttpRequest, QueryDict
from django.utils.translation import ugettext as _

from authentication_service import exceptions, api_helpers
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
                LOGGER.warning(
                    "User redirected off domain; " \
                    "(%s) -> (%s)." % (
                        current_host, parsed_url.netloc
                    )
                )

                # Clear theme cookie
                response.delete_cookie(COOKIES["ge_theme_middleware_cookie"])
                response.delete_cookie(COOKIES["redirect_cookie"])
                response.delete_cookie(COOKIES["redirect_client_name"])
                response.delete_cookie(COOKIES["redirect_client_terms"])

        return response


def fetch_theme(request, key=None):
    # Set get theme from either request or cookie. Request always wins to
    # ensure stale theme is not used.
    theme = request.GET.get("theme") or request.COOKIES.get(key)

    # In the event no theme has been found, try to check if theme is present in
    # a next query. This is to cater for the event where Django auth middleware
    # needed to redirect to login. Auth middleware redirects on the request
    # already.
    if theme is None:
        next_query = request.GET.get("next")

        # Only attempt to get the theme if there is a next query present, this
        # is the only known edge case we have to cater for.
        if next_query:
            next_query_args = parse_qs(urlparse(next_query).query)

            # Query values are in list form. Only grab the first value from the
            # list.
            theme = next_query_args.get("theme", [None])[0]

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
    client_terms_key = COOKIES["redirect_client_terms"]
    oidc_values = None

    @staticmethod
    def create_disabled_site_response(request):
        path_without_trailing_slash = request.path.rstrip("/")
        if path_without_trailing_slash == reverse("oidc_provider:authorize") and \
                request.method != "POST":
            authorize = AuthorizeEndpoint(request)
            try:
                authorize.validate_params()
            except (ClientIdError, RedirectUriError) as e:
                return render(
                    request,
                    "authentication_service/redirect_middleware_error.html",
                    {"error": e.error, "message": e.description},
                    status=500
                )
            except AuthorizeError as e:
                # Suppress one of the errors oidc raises. It is not required
                # for pages beyond login.
                if e.error == "unsupported_response_type":
                    pass
                else:
                    raise e

            site_is_active = api_helpers.is_site_active(authorize.client)
            if not site_is_active:
                return render(
                    request,
                    "authentication_service/redirect_middleware_error.html",
                    {
                        "error": _("Site access disabled"),
                        "message": _("The site you are trying to log in to has been disabled.")
                    },
                    status=403
                )

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Before storing the redirect_uri, ensure it comes from a valid client.
        # This is to prevent urls on other parts of the site being misused to
        # redirect users to none client apps.

        # Should the site be disabled we need to prevent login. This helper function
        # checks if (1) this is a login request and (2) if the client_id provided is
        # linked to a disabled site. If so, login is prevented by rendering a custom
        # page explaining that the site has been disabled.

        response = self.create_disabled_site_response(request)
        if response:
            return response

        uri = request.GET.get("redirect_uri", None)

        # To cut down on client lookups AuthorizeEndpoint does
        validator_uri = request.session.get(EXTRA_SESSION_KEY, {}).get(
            "redirect_uri_validation", None
        )
        if uri and request.method != "POST" and uri != validator_uri:
            authorize = AuthorizeEndpoint(request)
            try:
                authorize.validate_params()
            except (ClientIdError, RedirectUriError) as e:
                return render(
                    request,
                    "authentication_service/redirect_middleware_error.html",
                    {"error": e.error, "message": e.description},
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
            if self.oidc_values:
                request.session[EXTRA_SESSION_KEY] = {
                    self.client_name_key: authorize.client.name
                }
                request.session[EXTRA_SESSION_KEY][
                    self.client_terms_key] = authorize.client.terms_url
                request.session[EXTRA_SESSION_KEY] = {
                    "redirect_uri_validation": uri
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

            # Set Terms link
            response.set_cookie(
                self.client_terms_key,
                value=self.oidc_values.client.terms_url,
                httponly=True
            )
        return response


class ErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exc):
        if isinstance(exc, exceptions.BadRequestException):
            return HttpResponseBadRequest(exc.args)
