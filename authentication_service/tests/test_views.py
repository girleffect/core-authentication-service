import datetime
import random

from defender.utils import unblock_username
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from authentication_service.models import SecurityQuestion, \
    UserSecurityQuestion


class TestLockout(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestLockout, cls).setUpClass()
        cls.client = Client()

    def setUp(self):
        super(TestLockout, self).setUp()
        self.client = Client()

    def test_lockout(self):
        username = "unknown_user_{}".format(random.randint(0, 10000))
        login_url = reverse("login")
        login_data = {
            "login_view-current_step": "auth",
            "auth-username": username,
            "auth-password": "anything"
        }
        allowed_attempts = settings.DEFENDER_LOGIN_FAILURE_LIMIT
        attempt = 0
        while attempt < allowed_attempts:
            attempt += 1
            self.client.get(login_url)
            response = self.client.post(login_url, login_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.template_name,
                             ["authentication_service/login.html"])

        # The next (failed) attempt needs to prevent further login attempts
        self.client.get(login_url)
        response = self.client.post(login_url, login_data, follow=True)
        self.assertEqual([template.name for template in response.templates],
                         ["authentication_service/lockout.html",
                          "base.html"])

        # Manually unblock the username. This allows the user to try again.
        unblock_username(username)

        self.client.get(login_url)
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name,
                         ["authentication_service/login.html"])


class TestRegistrationView(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestRegistrationView, cls).setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(TestRegistrationView, cls).setUpTestData()

        # Security questions
        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

    def test_view_themes(self):
        response = self.client.get(reverse("registration") + "?theme=django")
        self.assertListEqual(
            response.template_name,
            [
                "authentication_service/registration/registration_django"
                ".html",
                "authentication_service/registration/registration.html"]
        )
        self.assertContains(response, "Girl Effect using django admin theme")

        response = self.client.get(reverse("registration") + "?theme=ge")
        self.assertListEqual(
            response.template_name,
            ["authentication_service/registration/registration_ge.html",
             "authentication_service/registration/registration.html"]
        )
        self.assertContains(response, "Girl Effect themed form")

    def test_view_success_redirects(self):
        # Test most basic iteration
        response = self.client.post(
            reverse("registration"),
            {
                "username": "Username",
                "password1": "password",
                "password2": "password",
                "birth_date": "2000-01-01",
                "email": "email@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/two-factor-auth/account/login/")

        # Test redirect url, no 2fa
        response = self.client.post(
            reverse("registration") + "?redirect_url=/test-redirect-url/",
            {
                "username": "Username1",
                "password1": "password",
                "password2": "password",
                "birth_date": "2000-01-01",
                "email": "email2@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/test-redirect-url/")

        # Test redirect url, 2fa
        response = self.client.post(
            reverse(
                "registration") +
            "?show2fa=true&redirect_url=/test-redirect-url/",
            {
                "username": "Username2",
                "password1": "password",
                "password2": "password",
                "birth_date": "2000-01-01",
                "email": "email3@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url,
                      "/two-factor-auth/account/two_factor/setup/")

        # Test redirect url, high security
        response = self.client.post(
            reverse(
                "registration") +
            "?security=high&redirect_url=/test-redirect-url/",
            {
                "username": "Username3",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "birth_date": "2000-01-01",
                "email": "email4@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url,
                      "/two-factor-auth/account/two_factor/setup/")

    def test_user_save(self):
        response = self.client.post(
            reverse("registration") + "?security=high",
            {
                "username": "Unique@User@Name",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "birth_date": "2000-01-01",
                "email": "emailunique@email.com",
                "msisdn": "0856545698",
                "age": "16",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url,
                      "/two-factor-auth/account/two_factor/setup/")
        user = get_user_model().objects.get(username="Unique@User@Name")
        self.assertEquals(user.email, "emailunique@email.com")
        self.assertEquals(user.msisdn, "0856545698")

    def test_security_questions_save(self):
        response = self.client.post(
            reverse("registration") + "?security=high",
            {
                "username": "Unique@User@Name",
                "age": "16",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "birth_date": "2000-01-01",
                "email": "emailunique@email.com",
                "msisdn": "0856545698",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-question": self.question_one.id,
                "form-0-answer": "Answer1",
                "form-1-question": self.question_two.id,
                "form-1-answer": "Answer2"
            }
        )
        self.assertIn(response.url,
                      "/two-factor-auth/account/two_factor/setup/")
        user = get_user_model().objects.get(username="Unique@User@Name")
        self.assertEquals(user.email, "emailunique@email.com")
        self.assertEquals(user.msisdn, "0856545698")
        question_one = UserSecurityQuestion.objects.get(
            question=self.question_one,
            language_code="en"
        )
        self.assertEquals(question_one.user, user)
        question_two = UserSecurityQuestion.objects.get(
            question=self.question_two,
            language_code="en"
        )
        self.assertEquals(question_two.user, user)

    def test_redirect_view(self):
        # Test without redirect cookie set.
        response = self.client.get(reverse("redirect_view"))
        self.assertIn(response.url, "/two-factor-auth/account/login/")

        # Test with redirect cookie set.
        self.client.cookies.load(
            {"register_redirect": "/test-redirect-after2fa/"})
        response = self.client.get(reverse("redirect_view"))
        self.assertIn(response.url, "/test-redirect-after2fa/")

    def test_incorrect_required_field_logger(self):
        test_output = [
            "WARNING:authentication_service.forms:"
            "Received required field that is "
            "not on form: someawesomefield",
            "WARNING:authentication_service.forms:"
            "Received required field that is "
            "not on form: notontheform"
        ]
        test_output.sort()
        with self.assertLogs(level="WARNING") as cm:
            self.client.get(
                reverse("registration") +
                "?requires=names"
                "&requires=picture"
                "&requires=someawesomefield"
                "&requires=notontheform"
            )
        output = cm.output
        output.sort()
        self.assertListEqual(output, test_output)

    def test_incorrect_hidden_field_logger(self):
        test_output = [
            "WARNING:authentication_service.forms:"
            "Received hidden field that is "
            "not on form: someawesomefield",
            "WARNING:authentication_service.forms:"
            "Received hidden field that is "
            "not on form: notontheform"
        ]
        test_output.sort()
        with self.assertLogs(level="WARNING") as cm:
            self.client.get(
                reverse("registration") +
                "?hide=end-user"
                "&hide=avatar"
                "&hide=someawesomefield"
                "&hide=notontheform"
            )
        output = cm.output
        output.sort()
        self.assertListEqual(output, test_output)


class EditProfileViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="testuser",
            email="wrong@email.com",
            password="Qwer!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.save()

        cls.twofa_user = get_user_model().objects.create_superuser(
            username="2fa_user", password="1234", email="2fa_user@test.com",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.twofa_user.save()

        cls.totp_device = TOTPDevice.objects.create(
            user=cls.twofa_user,
            name="default",
            confirmed=True,
            key=random_hex().decode()
        )

    def test_profile_edit(self):
        # Login user
        self.client.login(username="testuser", password="Qwer!234")

        # Get form
        response = self.client.get(
            "%s?redirect_url=/admin/" % reverse("edit_profile"))

        # Check 2FA isn't enabled
        self.assertNotContains(response, "2fa")

        # Post form
        response = self.client.post(
            "%s?redirect_url=/admin/" % reverse("edit_profile"),
            {
                "email": "test@user.com",
                "birth_date": "2001-01-01"
            },
        )
        updated = get_user_model().objects.get(username="testuser")

        self.assertEquals(updated.email, "test@user.com")
        self.assertRedirects(response, "/admin/")

    def test_2fa_link_enabled(self):
        # Login user
        self.client.login(username="2fa_user", password="1234")

        # Get form
        response = self.client.get(
            "%s?redirect_url=/admin/" % reverse("edit_profile"))

        # Check 2FA is enabled and present on edit page
        self.assertContains(response, "2fa")
