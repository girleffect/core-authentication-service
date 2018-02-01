from urllib.parse import urlparse

from django.utils.deprecation import MiddlewareMixin


class OIDCSessionManagementMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 302:
            current_host = request.get_host()
            location = response.get("Location", "")
            parsed_url = urlparse(location)
            if parsed_url.netloc != "" and current_host != parsed_url.netloc:
                request.session.flush()
        return response
