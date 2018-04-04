import datetime

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from oidc_provider.models import Client

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

    def test_session_flush_logger(self):
        with self.assertLogs(level="WARNING") as cm:
            self.client.cookies.load(
                {"ge_redirect_cookie": "http://nuked-session.com/logging/test-redirect/"})
            self.client.get(reverse("redirect_view"))
            test_output = [
                "WARNING:authentication_service.middleware:" \
                "User redirected off domain; " \
                "(testserver) -> (nuked-session.com). Session flushed."
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
