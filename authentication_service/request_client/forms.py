from django import forms

from authentication_service.request_client import models


class RequestClientForm(forms.ModelForm):
    class Meta:
        model = models.RequestedClient
        fields = [
            "name", "client_type", "response_type", "jwt_alg",
            "website_url", "terms_url", "contact_email", "logo",
            "reuse_consent"
        ]
