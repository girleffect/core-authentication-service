import datetime
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils.translation import activate

from oidc_provider.models import Client

from authentication_service import constants, exceptions


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
        with self.assertRaises(exceptions.BadRequestException) as e:
            response = self.client.get(
                reverse(
                    "registration"
                ) + "?redirect_uri=http%3A%2F%2Fexample.com%2F"
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
        activate("fr")

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
        self.assertRedirects(
            response, f"{reverse('login')}" \
            "?next=/openid/authorize%3Ftheme%3Dspringster%26response_type" \
            "%3Dcode%26scope%3Dopenid%26client_id%3Dclient_id_1" \
            "%26redirect_uri%3Dhttp%253A%252F%252Fexample.com%252F"
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
    def test_login_theme_with_trailingslash(self, mocked_is_site_active):
        mocked_is_site_active.return_value = True
        response = self.client.get(
            "/openid/authorize/" \
            "?theme=springster&response_type=code&scope=openid&client_id=client_id_1&" \
            "redirect_uri=http%3A%2F%2Fexample.com%2F",
            follow=True
        )
        self.assertRedirects(
            response, f"{reverse('login')}" \
            "?next=/openid/authorize/%3Ftheme%3Dspringster%26response_type" \
            "%3Dcode%26scope%3Dopenid%26client_id%3Dclient_id_1" \
            "%26redirect_uri%3Dhttp%253A%252F%252Fexample.com%252F"
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


class TestLanguageUpdateMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestLanguageUpdateMiddleware, cls).setUpTestData()
        cls.client_obj = Client(
            name="test_langauge_client",
            client_id="client_id_langauge",
            client_secret="super_client_secret_5",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=["http://example_one.com/"],
            terms_url="http://example-terms.com"
        )
        cls.client_obj.save()

    def test_language_update(self):
        response = self.client.get(
            reverse(
                "login"
            ) + "?language=prs&theme=zathu&required=username",
            follow=True
        )
        self.assertRedirects(
            response, "/prs/login/?theme=zathu&required=username"
        )
        self.assertContains(response, "THIS IS JUST FOR UNITTESTS ATM")

    def test_missing_language_update(self):
        response = self.client.get(
            reverse(
                "login"
            ) + "?language=rts&theme=zathu&required=username",
            follow=True
        )
        self.assertEquals(
            response.status_code, 404
        )

    @override_settings(ACCESS_CONTROL_API=MagicMock())
    def test_none_i18n_urls(self):
        response = self.client.get(
            reverse(
                "oidc_provider:authorize"
            ) + "?response_type=code&scope=openid&client_id=client_id_langauge&"
                "redirect_uri=http%3A%2F%2Fexample_one.com%2F&language=prs",
            follow=True
        )
        response = self.client.get(
            response.redirect_chain[-1][0],
            follow=True
        )
        self.assertEquals(
            response.request["PATH_INFO"],
            "/prs/login/"
        )
        self.assertEquals(
            response.request["QUERY_STRING"],
            "next=%2Fopenid%2Fauthorizeresponse_type%3D%255B%2527code%2527%255D%26scope%3D%255B%2527openid%2527%255D%26client_id%3D%255B%2527client_id_langauge%2527%255D%26redirect_uri%3D%255B%2527http%253A%252F%252Fexample_one.com%252F%2527%255D"
        )
        response = self.client.get(
            "/login/?language=prs",
            follow=True
        )

        """
        redirect_chain = [('/en/login/?language=prs', 302), ('/prs/login/', 302)]
        """
        self.assertRedirects(
            response,
            "/prs/login/"
        )
