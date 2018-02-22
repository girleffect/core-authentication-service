from urllib.parse import urlparse
import logging

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
        if theme:
            templates = {"original": [], "new": []}
            for path in response.template_name:
                file_name = path[path.rindex("/")+1:]
                dir_path = path[:path.rindex("/")+1]
                extension = file_name[file_name.rindex("."):]
                name = "%s_%s%s" % (
                    file_name[:file_name.rindex(extension)], theme, extension)
                templates["new"].append({"name": name, "path": dir_path})
                templates["original"].append(file_name)

            joined_names = ",".join(templates["original"])
            for template in templates["new"]:
                prepend_list = []
                if template["name"] not in joined_names:
                    prepend_list.append("%s%s" % (
                        template["path"], template["name"]))
                response.template_name = prepend_list + response.template_name
        return response
