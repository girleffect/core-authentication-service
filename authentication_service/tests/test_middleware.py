from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from oidc_provider.models import Client


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
        )
        cls.user.set_password("P0ppy")
        cls.user.save()

    def test_session_flush(self):
        # Log user in to bypass need for extra login form post.
        self.client.login(username=self.user.username, password="P0ppy")
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?client_id=client_id_1&redirect_uri=http%3A%2F%2Fexample.com%2F&response_type=code",
            follow=True
        )

        # Ensure its a 200 response.
        self.assertEqual(response.status_code, 200)

        # Ensure there is indeed auth data on the session.
        self.assertIn("_auth_user_id", self.client.session.keys())
        response = self.client.post(
            reverse(
                "oidc_provider:authorize"
            ),
            {
                "allow": "Authorize",
                "client_id": "client_id_1",
                "redirect_uri": "http://example.com/",
                "scope": "openid+email",
                "response_type": "code"
            },
        )

        # Make sure session is flushed.
        self.assertEqual(len(self.client.session.items()), 0)

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
                {"register_redirect": "http://nuked-session.com/logging/test-redirect/"})
            self.client.get(reverse("redirect_view"))
            test_output = [
                "WARNING:authentication_service.middleware:" \
                "User redirected off domain; " \
                "(testserver) -> (nuked-session.com). Session flushed."
            ]
            output = cm.output
            self.assertListEqual(output, test_output)
