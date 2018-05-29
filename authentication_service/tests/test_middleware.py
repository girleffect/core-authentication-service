import datetime
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from oidc_provider.models import Client

from authentication_service import constants


class TestSessionMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestSessionMiddleware, cls).setUpTestData()
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
    def test_session_flush_logger(self):
        with self.assertLogs(level="WARNING") as cm:
            Client.objects.create(
                client_id="nuker",
                name= "CopiedRegistrationMigrationClient",
                client_secret= "super_client_secret_9",
                response_type= "code",
                jwt_alg= "HS256",
                redirect_uris= ["http://nuked-session.com/logging/test-redirect/"],
                terms_url="http://registration-terms.com"
            )
            response = self.client.get(
                reverse(
                    "registration"
                ) + "?client_id=nuker&redirect_uri=http://nuked-session.com/logging/test-redirect/",
            )
            response = self.client.get(
                reverse(
                    "redirect_view"
                )
            )
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
            redirect_uris=["http://example.com/"],
            terms_url="http://example-terms.com"
        )
        cls.client_obj.save()

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_session_values(self):
        response = self.client.get(
            reverse(
                "registration"
            ) + "?client_id=client_id_1&" \
            "redirect_uri=http%3A%2F%2Fexample.com%2F&response_type=code",
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.CLIENT_NAME],
            self.client_obj.name
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.CLIENT_URI],
            "http://example.com/"
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.CLIENT_NAME],
            self.client_obj.name
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_context_values(self):
        response = self.client.get(
            reverse(
                "registration"
            ) + "?client_id=client_id_1&" \
            "redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], "http://example.com/"
        )
        self.assertEquals(
            response.context["ge_global_client_name"], self.client_obj.name
        )
        response = self.client.get(
            reverse(
                "registration"
            )
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], None
        )
        self.assertEquals(
            response.context["ge_global_client_name"], None
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_client_id_and_redirect_uri_validation(self):
        response = self.client.get(
            reverse(
                "registration"
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
                "oidc_provider:authorize"
            ) + "?response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEqual(response.status_code, 302)

        # When the site matching the client_id is inactive, access is forbidden.
        mocked_is_site_active.return_value = False
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEqual(
            response.templates[0].name,
            "authentication_service/redirect_middleware_error.html"
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_login_session(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F",
            follow=True
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], "http://example.com/"
        )
        self.assertEquals(
            response.context["ge_global_client_name"], self.client_obj.name
        )
        self.assertEquals(
            response.context["ge_global_client_terms"],
            self.client_obj.terms_url
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_registration_session(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "registration"
            ) + "?response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F"
        )
        self.assertEquals(
            response.context["ge_global_redirect_uri"], "http://example.com/"
        )
        self.assertEquals(
            response.context["ge_global_client_name"], self.client_obj.name
        )
        self.assertEquals(
            response.context["ge_global_client_terms"],
            self.client_obj.terms_url
        )


class TestThemeMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestThemeMiddleware, cls).setUpTestData()
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
        cls.user.set_password("D4isy")
        cls.user.save()

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_login_theme(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?theme=springster&response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F",
            follow=True
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.THEME],
            "springster"
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="springster" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_registration_theme(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "registration"
            ) + "?theme=ninyampinga"
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.THEME],
            "ninyampinga"
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="ninyampinga" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_edit_theme(self, mocked_is_site_active):
        self.client.login(username=self.user.username, password="D4isy")
        response = self.client.get(
            reverse(
                "edit_profile"
            ) + "?theme=zathu"
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.THEME],
            "zathu"
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="zathu" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_login_theme_clear(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?theme=springster&response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F",
            follow=True
        )
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?response_type=code&scope=openid&client_id=client_id_1&"
                "redirect_uri=http%3A%2F%2Fexample.com%2F",
            follow=True
        )
        self.assertEquals(
            self.client.session.get(
                constants.EXTRA_SESSION_KEY, {}).get(
                    constants.SessionKeys.THEME),
            None
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="None" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_registration_theme_clear(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "registration"
            ) + "?theme=ninyampinga"
        )
        response = self.client.get(
            reverse(
                "registration"
            )
        )
        self.assertEquals(
            self.client.session.get(
                constants.EXTRA_SESSION_KEY, {}).get(
                    constants.SessionKeys.THEME),
            None
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="None" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_edit_theme_clear(self, mocked_is_site_active):
        self.client.login(username=self.user.username, password="D4isy")
        response = self.client.get(
            reverse(
                "edit_profile"
            ) + "?theme=zathu"
        )
        response = self.client.get(
            reverse(
                "edit_profile"
            )
        )
        self.assertEquals(
            self.client.session.get(
                constants.EXTRA_SESSION_KEY, {}).get(
                    constants.SessionKeys.THEME),
            None
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="None" />'
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    @patch("authentication_service.api_helpers.is_site_active")
    def test_registration_theme_override(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            reverse(
                "registration"
            ) + "?theme=ninyampinga"
        )
        response = self.client.get(
            reverse(
                "registration"
            ) + "?theme=springster"
        )
        self.assertEquals(
            self.client.session[
                constants.EXTRA_SESSION_KEY][
                    constants.SessionKeys.THEME],
            "springster"
        )
        self.assertContains(
            response,
            '<div id="ge-template-theme" name="springster" />'
        )
