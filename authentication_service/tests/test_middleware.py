import datetime
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from oidc_provider.models import Client

from access_control import Site
from authentication_service import constants


class TestOIDCSessionMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestOIDCSessionMiddleware, cls).setUpTestData()
        cls.client = Client(
            name="test_client",
            client_id="client_id_1",
            client_secret="super_client_secret_1",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=["http://example.com/"]
        )
        cls.client.save()

        cls.user = get_user_model().objects.create(
            username="Lilly",
            birth_date=datetime.date(2000, 1, 1)
        )
        cls.user.set_password("P0ppy")
        cls.user.save()

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_redirect_view(self):
        self.client.login(username=self.user.username, password="P0ppy")
        # Ensure there is indeed auth data on the session.
        self.assertIn("_auth_user_id", self.client.session.keys())
        # Test with redirect cookie set.
        self.client.cookies.load(
            {"register_redirect": "http://somecoolsite.com/test-redirect/"})
        response = self.client.get(reverse("redirect_view"))

        # Make sure session is flushed.
        self.assertEqual(len(self.client.session.items()), 0)

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_session_flush_logger(self):
        with self.assertLogs(level="WARNING") as cm:
            self.client.cookies.load(
                {"ge_redirect_cookie": "http://nuked-session.com/logging/test-redirect/"})
            self.client.get(reverse("redirect_view"))
            test_output = [
                "WARNING:authentication_service.middleware:" \
                "User redirected off domain; " \
                "(testserver) -> (nuked-session.com)."
            ]
            output = cm.output
            self.assertListEqual(output, test_output)


class TestRedirectManagementMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestRedirectManagementMiddleware, cls).setUpTestData()
        cls.client_obj = Client(
            name="test_client",
            client_id="client_id_1",
            client_secret="super_client_secret_1",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=["http://example.com/"]
        )
        cls.client_obj.save()

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_cookie_and_session_values(self):
        response = self.client.get(
            reverse(
                "login"
            ) + "?client_id=client_id_1&" \
            "redirect_uri=http%3A%2F%2Fexample.com%2F&response_type=code",
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.COOKIES["redirect_client_name"]],
            self.client_obj.name
        )
        self.assertEquals(
            response.client.cookies[constants.COOKIES["redirect_cookie"]].value,
            "http://example.com/"
        )
        self.assertEquals(
            response.client.cookies[
                constants.COOKIES["redirect_client_name"]].value,
            self.client_obj.name
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_context_values(self):
        response = self.client.get(
            reverse(
                "login"
            ) + "?client_id=client_id_1&" \
            "redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], None
        )
        self.assertEquals(
            response.context["ge_global_client_name"], self.client_obj.name
        )
        self.client.cookies.load(
            {"ge_redirect_cookie": "http://example.com/",
            "ge_oidc_client_name": self.client_obj.name}
        )
        response = self.client.get(
            reverse(
                "login"
            )
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], "http://example.com/"
        )
        self.assertEquals(
            response.context["ge_global_client_name"], self.client_obj.name
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_client_id_and_redirect_uri_validation(self):
        response = self.client.get(
            reverse(
                "login"
            ) + "?redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.context["error"], "Client ID Error")
        self.assertEqual(
            response.context["message"],
            "The client identifier (client_id) is missing or invalid."
        )
        self.assertEqual(
            response.templates[0].name,
            "authentication_service/redirect_middleware_error.html"
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_disabled_site(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "login"
            ) + "?next=/openid/authorize/%3Fresponse_type%3Dcode%26scope%3Dopenid%26client_id"
                "%3Dclient_id_1%26redirect_uri%3Dhttp%253A%252F%252Fexample.com%252F"
        )
        self.assertEqual(response.status_code, 200)

        # When the site matching the client_id is inactive, access is forbidden.
        mocked_is_site_active.return_value = False
        response = self.client.get(
            reverse(
                "login"
            ) + "?next=/openid/authorize/%3Fresponse_type%3Dcode%26scope%3Dopenid%26client_id"
                "%3Dclient_id_1%26redirect_uri%3Dhttp%253A%252F%252Fexample.com%252F"
        )
        self.assertEqual(
            response.templates[0].name,
            "authentication_service/redirect_middleware_error.html"
        )
        self.assertEqual(response.status_code, 403)
