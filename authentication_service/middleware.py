from urllib.parse import urlparse
import logging
import os

from oidc_provider.lib.endpoints.authorize import AuthorizeEndpoint
from oidc_provider.lib.errors import (
    ClientIdError,
    RedirectUriError
)


from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


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
    def process_response(self, request, response):
        if response and response.status_code == 302:
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
        return response


class ThemeManagementMiddleware(MiddlewareMixin):
    cookie_key = "ge_theme_middleware_cookie"

    def process_template_response(self, request, response):
        theme = request.GET.get("theme", None) or request.COOKIES.get(
            self.cookie_key)
        if theme:
            response.set_cookie(
                self.cookie_key, value=theme, httponly=True
            )
            templates = {"original": [], "new": []}
            for full_path in response.template_name:
                path, filename = os.path.split(full_path)
                filename, extension = os.path.splitext(filename)
                name = "%s_%s%s" % (filename, theme, extension)
                templates["new"].append({"name": name, "path": path})
                templates["original"].append(filename)

            joined_names = ",".join(templates["original"])
            for template in templates["new"]:
                prepend_list = []
                if template["name"] not in joined_names:
                    prepend_list.append(
                        os.path.join(template["path"], template["name"]))
                response.template_name = prepend_list + response.template_name
        return response


class RedirectManagementMiddleware(MiddlewareMixin):
    cookie_key = "ge_redirect_middleware_cookie"

    # TODO refactor the redirect cookie view as well as other views that set the cookie.
    def process_response(self, request, response):
        # Before storing the redirect_uri, ensure it comes from a valid client.
        # This is to prevent urls on other parts of the site being misused to
        # redirect users to none client apps.
        uri = request.GET.get("redirect_uri", None)
        if uri:
            authorize = AuthorizeEndpoint(request)
            try:
                authorize.validate_params()
            except (ClientIdError, RedirectUriError) as e:
                # TODO User friendly error message
                return render(
                    request,
                    "authentication_service/redirect_middleware_error.html",
                    {"error": e.error, "message": e.description},
                    status=500
                )
            response.set_cookie(
                self.cookie_key, value=authorize.params["redirect_uri"], httponly=True
            )
        return response
