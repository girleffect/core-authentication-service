import datetime

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from unittest.mock import patch

from authentication_service.request_client.models import RequestedClient


class TestRequest(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = get_user_model().objects.create_superuser(
            username="testuser",
            email="an@email.com",
            password="Qwer!234",
            birth_date=datetime.date(2001, 12, 12)
        )

    def test_default_errors(self):
        self.client.login(username="testuser", password="Qwer!234")
        response = self.client.post(
            reverse("request_client:request_form"),
        )
        self.assertEqual(
            response.context["form"].errors,
            {
                "name": ["This field is required."],
                "client_type": ["This field is required."],
                "response_type": ["This field is required."],
                "jwt_alg": ["This field is required."],
                "redirect_uris": ["This field is required."],
                "website_url": ["This field is required."]
            }
        )

    @patch("authentication_service.tasks.send_mail.apply_async")
    def test_client_request(self, send_mail):
        self.client.login(username="testuser", password="Qwer!234")
        response = self.client.post(
            reverse("request_client:request_form"),
            data={
                "name": "Test-client",
                "client_type": "confidential",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": "aaaa.com",
                "website_url": "www.google.com",
            }
        )
        client = RequestedClient.objects.get(name="Test-client")
        send_mail.assert_called_with(
            kwargs={
                "context": {},
                "mail_type": "request_client_creation",
                "objects_to_fetch": [{
                    "app_label": "request_client",
                    "model": "requestedclient",
                    "id": client.id,
                    "context_key": "requested_client"
                }]
            }
        )
