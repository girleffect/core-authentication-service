from django import forms

from authentication_service.request_client import models


class RequestClientForm(forms.ModelForm):
    class Meta:
        model = models.RequestedClient
        fields = [
            "name", "client_environment", "client_type", "response_type",
            "jwt_alg", "redirect_uris", "post_logout_redirect_uris",
            "website_url", "terms_url", "contact_email", "logo",
            "reuse_consent", "scope"
        ]
