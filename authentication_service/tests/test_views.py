import datetime
import random

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth import hashers
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from unittest.mock import patch
from defender.utils import unblock_username

from authentication_service.models import SecurityQuestion, \
    UserSecurityQuestion

from authentication_service.tests.models import TemporaryUserStore


class TestLogin(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestLogin, cls).setUpTestData()
        cls.user = get_user_model().objects.create_user(
            username="inactiveuser1",
            email="inactive@email.com",
            password="Qwer!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.is_active = False
        cls.user.save()

    def test_inactive_user_login(self):
        data = {
            "login_view-current_step": "auth",
            "auth-username": "inactiveuser1",
            "auth-password": "Qwer!234"
        }
        response = self.client.post(
            reverse("login"),
            data=data,
            follow=True
        )
        self.assertContains(response, "Your account has been deactivated. Please contact support.")

    def test_active_user_login(self):
        self.user.is_active = True
        self.user.save()

        data = {
            "login_view-current_step": "auth",
            "auth-username": "inactiveuser1",
            "auth-password": "Qwer!234"
        }
        response = self.client.post(
            reverse("login"),
            data=data,
            follow=True
        )
        self.assertRedirects(response, "{}?next=%2Fen%2Fadmin%2F".format(reverse("login")))

    def test_migrated_user_login(self):
        # TODO move import and data creation once finalised.
        temp_user = TemporaryUserStore.objects.create(
            username="migrateduser",
            email="inactive@email.com",
        )
        temp_user.set_password("Qwer!234")

        data = {
            "login_view-current_step": "auth",
            "auth-username": temp_user.username,
            "auth-password": "Qwer!234"
        }
        response = self.client.post(
            reverse("login"),
            data=data,
            follow=True
        )
        self.assertIn(
            "/migrate/",
            response.redirect_chain[-1][0],
        )
        self.assertIn(
            "/userdata/",
            response.redirect_chain[-1][0],
        )
        self.assertEqual(
            response.redirect_chain[-1][1],
            302,
        )


class TestMigration(TestCase):
    """
    Test urls can be handled a bit better, however this was the fastest way
    to refactor the existing tests.
    """

    # Wizard helper methods
    def do_login(self, data):
        return self.client.post(
            reverse("login"),
            data=data,
            follow=True
        )

    @classmethod
    def setUpTestData(cls):
        super(TestMigration, cls).setUpTestData()
        cls.temp_user = TemporaryUserStore.objects.create(
            username="coolmigrateduser",
            email="migrater@email.com",
        )
        cls.temp_user.set_password("Qwer!234")
        cls.user = get_user_model().objects.create_user(
            username="existinguser",
            email="existing@email.com",
            birth_date=datetime.date(2001, 1, 1),
            password="Qwer!234"
        )
        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

    def test_userdata_step(self):
        # Login and get the response url
        data = {
            "login_view-current_step": "auth",
            "auth-username": self.temp_user.username,
            "auth-password": "Qwer!234"
        }

        response = self.do_login(data)
        # Default required
        data = {
            "migrate_user_wizard-current_step": "userdata"
        }

        response = self.client.post(
            response.redirect_chain[-1][0],
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["wizard"]["steps"].current, "userdata"
        )
        self.assertEqual(
            response.context["wizard"]["form"].errors,
            {"username": ["This field is required."],
            'age': ["This field is required."]}
        )

        # Username unique
        data = {
            "migrate_user_wizard-current_step": "userdata",
            "userdata-username": self.user.username,
            "userdata-age": 20
        }
        response = self.client.post(
            response._request.path,
            data=data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["wizard"]["steps"].current, "userdata"
        )
        self.assertEqual(
            response.context["wizard"]["form"].errors,
            {"username": ["A user with that username already exists."]}
        )
        self.assertContains(
            response, "A user with that username already exists."
        )

    def test_securityquestion_step(self):
        # Login and get the response url
        data = {
            "login_view-current_step": "auth",
            "auth-username": self.temp_user.username,
            "auth-password": "Qwer!234"
        }

        response = self.do_login(data)
        # Username unique
        data = {
            "migrate_user_wizard-current_step": "userdata",
            "userdata-username": "newusername",
            "userdata-age": 20
        }
        response = self.client.post(
            response.redirect_chain[-1][0],
            data=data,
        )
        response = self.client.get(response.url)
        data = {
            "migrate_user_wizard-current_step": "securityquestions",
            "securityquestions-TOTAL_FORMS": 2,
            "securityquestions-INITIAL_FORMS": 0,
            "securityquestions-MIN_NUM_FORMS": 0,
            "securityquestions-MAX_NUM_FORMS": 1000,
        }
        response = self.client.post(
            response._request.path,
            data=data,
        )

        self.assertEqual(
            response.context["wizard"]["form"].non_form_errors(),
            ["Please fill in all Security Question fields."]
        )
        self.assertContains(
            response, "Please fill in all Security Question fields."
        )

        data = {
            "migrate_user_wizard-current_step": "securityquestions",
            "securityquestions-TOTAL_FORMS": 2,
            "securityquestions-INITIAL_FORMS": 0,
            "securityquestions-MIN_NUM_FORMS": 0,
            "securityquestions-MAX_NUM_FORMS": 1000,
            "securityquestions-0-question": self.question_one.id,
            "securityquestions-0-answer": "Answer1",
            "securityquestions-1-question": self.question_one.id,
            "securityquestions-1-answer": "Answer2"
        }
        response = self.client.post(
            response._request.path,
            data=data,
        )
        self.assertEqual(
            response.context["wizard"]["form"].non_form_errors(),
            ["Each question can only be picked once."]
        )
        self.assertContains(
            response, "Each question can only be picked once."
        )

    def test_migration_step(self):
        # Login and get the response url
        data = {
            "login_view-current_step": "auth",
            "auth-username": self.temp_user.username,
            "auth-password": "Qwer!234"
        }

        response = self.do_login(data)
        # Username unique
        data = {
            "migrate_user_wizard-current_step": "userdata",
            "userdata-username": "newusername",
            "userdata-age": 20
        }
        response = self.client.post(
            response.redirect_chain[-1][0],
            data=data,
            follow=True
        )
        data = {
            "migrate_user_wizard-current_step": "securityquestions",
            "securityquestions-TOTAL_FORMS": 2,
            "securityquestions-INITIAL_FORMS": 0,
            "securityquestions-MIN_NUM_FORMS": 0,
            "securityquestions-MAX_NUM_FORMS": 1000,
            "securityquestions-0-question": self.question_one.id,
            "securityquestions-0-answer": "Answer1",
            "securityquestions-1-question": self.question_two.id,
            "securityquestions-1-answer": "Answer2"
        }
        self.assertEqual(get_user_model().objects.filter(
            username=self.temp_user.username).count(), 0
        )
        response = self.client.post(
            response._request.path,
            data=data,
            follow=True
        )
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(get_user_model().objects.filter(
            username="newusername").count(), 1
        )



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
            self.assertIn("authentication_service/login.html",
                          response.template_name)

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
        self.assertIn("authentication_service/login.html",
                      response.template_name)


class TestSecurityQuestionLockout(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestSecurityQuestionLockout, cls).setUpTestData()
        cls.user = get_user_model().objects.create_user(
            username="user_who_forgot_creds",
            password="Qwer!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.save()

        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

        cls.user_answer_one = UserSecurityQuestion.objects.create(
            question=cls.question_one,
            user=cls.user,
            answer="right"
        )
        cls.user_answer_two = UserSecurityQuestion.objects.create(
            question=cls.question_two,
            user=cls.user,
            answer="right"
        )

    def test_lockout_on_reset(self):
        session = self.client.session
        session["lookup_user_id"] = str(self.user.id)
        session.save()

        username = "unknown_user_{}".format(random.randint(0, 10000))
        reset_url = reverse("reset_password_security_questions")
        reset_data = {
            "login_view-current_step": "auth",
            "auth-username": username,
            "question_%s" % self.user_answer_one.id: "test",
            "question_%s" % self.user_answer_two.id: "answer"
        }
        allowed_attempts = settings.DEFENDER_LOGIN_FAILURE_LIMIT
        attempt = 0

        while attempt < allowed_attempts:
            attempt += 1
            self.client.get(reset_url)
            response = self.client.post(reset_url, reset_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                "authentication_service/reset_password/security_questions.html",
                response.template_name
            )

        self.client.get(reset_url)
        response = self.client.post(reset_url, reset_data, follow=True)
        self.assertEqual([template.name for template in response.templates],
                         ["authentication_service/lockout.html",
                          "base.html"])

        unblock_username(username)

        self.client.get(reset_url)
        response = self.client.post(reset_url, reset_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "authentication_service/reset_password/security_questions.html",
            response.template_name
        )


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

    def test_view_success_redirects(self):
        # Test most basic iteration
        response = self.client.post(
            reverse("registration"),
            {
                "username": "Username",
                "password1": "password",
                "password2": "password",
                "age": "18",
                "birth_date": "2000-01-01",
                "terms": True,
                "email": "email@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("login"))

        # Test most basic registration with age instead of birth_date
        response = self.client.post(
            reverse("registration"),
            {
                "username": "Username0",
                "password1": "password",
                "password2": "password",
                "age": "16",
                "terms": True,
                "email": "email1@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("login"))

        # Test most basic registration with age and birth_date. Birth_date takes precedence.
        response = self.client.post(
            reverse("registration"),
            {
                "username": "Username0a",
                "password1": "password",
                "password2": "password",
                "birth_date": "1999-01-01",
                "age": "16",
                "terms": True,
                "email": "email1a@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("login"))

        # Test redirect url, no 2fa
        self.client.cookies.load(
            {"ge_redirect_cookie": "/test-redirect-url/"})
        response = self.client.post(
            reverse("registration") + "?redirect_uri=/test-redirect-url/",
            {
                "username": "Username1",
                "password1": "password",
                "password2": "password",
                "age": "18",
                "terms": True,
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
            "?show2fa=true&redirect_uri=/test-redirect-url/",
            {
                "username": "Username2",
                "password1": "password",
                "password2": "password",
                "age": "18",
                "terms": True,
                "birth_date": "2000-01-01",
                "email": "email3@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("two_factor_auth:setup"))

        # Test redirect url, high security
        response = self.client.post(
            reverse(
                "registration") +
            "?security=high&redirect_uri=/test-redirect-url/",
            {
                "username": "Username3",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "age": "18",
                "terms": True,
                "birth_date": "2000-01-01",
                "email": "email4@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("two_factor_auth:setup"))

    def test_user_save(self):
        response = self.client.post(
            reverse("registration") + "?security=high",
            {
                "username": "Unique@User@Name",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "birth_date": "2000-01-01",
                "terms": True,
                "email": "emailunique@email.com",
                "msisdn": "0856545698",
                "age": "16",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, reverse("two_factor_auth:setup"))
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
                "terms": True,
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
        self.assertIn(response.url, reverse("two_factor_auth:setup"))
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
        self.assertIn(response.url, reverse("login"))

        # Test with redirect cookie set.
        self.client.cookies.load(
            {"ge_redirect_cookie": "/test-redirect-after2fa/"})
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

    def test_view_terms_html(self):
        response = self.client.get(
            reverse("registration")
        )
        self.assertContains(response, '<a href="https://www.girleffect.org/'\
        'terms-and-conditions/">Click here to view the terms and conditions</a>'
        )
        self.client.cookies.load(
            {"ge_oidc_client_terms": "http://www.example.com"}
        )
        response = self.client.get(
            reverse("registration")
        )
        self.assertContains(response, '<a href="http://www.example.com">'\
        'Click here to view the terms and conditions</a>'
        )


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

        # Security questions
        cls.text_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.text_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

        cls.question_one = UserSecurityQuestion.objects.create(
            user=cls.user,
            question=cls.text_one,
            language_code="en",
            answer="Answer1"
        )
        cls.question_two = UserSecurityQuestion.objects.create(
            user=cls.user,
            question=cls.text_two,
            language_code="en",
            answer="Answer2"
        )

    def test_profile_edit(self):
        # Login user
        self.client.login(username="testuser", password="Qwer!234")

        # Get form
        response = self.client.get(
            reverse("edit_profile"))

        # Check 2FA isn't enabled
        self.assertNotContains(response, "2fa")

        # Post form
        self.client.cookies.load(
            {"ge_redirect_cookie": reverse("admin:index")})
        response = self.client.post(
            "%s?redirect_uri=/admin/" % reverse("edit_profile"),
            {
                "email": "test@user.com",
                "birth_date": "2001-01-01"
            },
        )
        updated = get_user_model().objects.get(username="testuser")

        self.assertEquals(updated.email, "test@user.com")
        self.assertRedirects(response, reverse("admin:index"))

    def test_2fa_link_enabled(self):
        # Login user
        self.client.login(username="2fa_user", password="1234")

        # Get form
        response = self.client.get(
            reverse("edit_profile")
        )

        # Check 2FA is enabled and present on edit page
        self.assertContains(response, "2fa")

    def test_security_questions_update(self):
        self.client.login(username=self.user.username, password="Qwer!234")
        response = self.client.post(
            reverse("update_security_questions"),
            {
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "2",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-question": self.text_one.id,
                "form-0-answer": "AnswerFirst",
                "form-0-id": self.question_one.id,
                "form-1-question": self.text_two.id,
                "form-1-answer": "AnswerSecond",
                "form-1-id": self.question_two.id,
            },
        )
        question_one = UserSecurityQuestion.objects.get(
            id=self.question_one.id
        )
        question_two = UserSecurityQuestion.objects.get(
            id=self.question_two.id
        )
        self.assertTrue(hashers.check_password(
            "AnswerFirst".lower(),
            question_one.answer)
        )
        self.assertTrue(hashers.check_password(
            "AnswerSecond".lower(),
            question_two.answer)
        )


class ResetPasswordTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="identifiable_user", email="user@id.com",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.set_password("1234")
        cls.user.save()

        cls.user_no_email = get_user_model().objects.create(
            username="user_no_email",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.set_password("1234")
        cls.user.save()

        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

        cls.user_answer_one = UserSecurityQuestion.objects.create(
            user=cls.user_no_email, question=cls.question_one,
            language_code="en", answer="one"
        )

        cls.user_answer_two = UserSecurityQuestion.objects.create(
            user=cls.user_no_email, question=cls.question_two,
            language_code="en", answer="two"
        )

    def test_username_as_identifier(self):
        response = self.client.post(
            reverse("reset_password"),
            data={
                "email": "user_no_email"
            }
        )
        self.assertRedirects(
            response, reverse("reset_password_security_questions"))

    @patch("authentication_service.tasks.send_mail.apply_async")
    def test_email_as_identifier(self, send_mail):
        response = self.client.post(
            reverse("reset_password"),
            data={
                "email": "user@id.com"
            }
        )
        send_mail.assert_called()
        self.assertNotIn("User not found", response)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("password_reset_done"))

    def test_user_not_found(self):
        response = self.client.post(
            reverse("reset_password"),
            data={
                "email": "identifiable_user2"
            }
        )
        self.assertRedirects(response, reverse("password_reset_done"))

        response = self.client.post(
            reverse("reset_password"),
            data={
                "email": "user2@id.com"
            }
        )
        self.assertRedirects(response, reverse("password_reset_done"))

    def test_security_question_reset(self):
        # Explicity set a session variable to access
        session = self.client.session
        session["lookup_user_id"] = str(self.user_no_email.id)
        session.save()

        response = self.client.get(
            reverse("reset_password_security_questions")
        )
        self.assertContains(response, "question_%s" % self.user_answer_one.id)
        self.assertContains(response, "question_%s" % self.user_answer_two.id)

        response = self.client.post(
            reverse("reset_password_security_questions"),
            data={
                "question_%s" % self.user_answer_one.id: "one",
                "question_%s" % self.user_answer_two.id: "three"
            }
        )
        self.assertContains(response, "One or more answers are incorrect")

        response = self.client.post(
            reverse("reset_password_security_questions"),
            data={
                "question_%s" % self.user_answer_one.id: "one",
                "question_%s" % self.user_answer_two.id: "two"
            }
        )

        # Redirects to password reset confirm view
        self.assertEquals(response.status_code, 302)

class DeleteAccountTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="leaving_user", email="awol@id.com",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.set_password("atleast_its_not_1234")
        cls.user.save()

    def test_view_html_toggle(self):
        self.client.login(username=self.user.username, password="atleast_its_not_1234")
        response = self.client.get(reverse("delete_account"))
        self.assertNotContains(response, "confirmed_deletion")
        response = self.client.post(
            reverse("delete_account"),
            data={
                "reason": "The theme is ugly"
            }
        )
        self.assertContains(
            response,
            "<input name=\"confirmed_deletion\" type=\"submit\" value=\"Yes\" class=\"Button\" />"
        )
        self.assertContains(response,
            "<textarea name=\"reason\" cols=\"40\" rows=\"10\" id=\"id_reason\" class=\" Textarea \">"
        )

    @patch("authentication_service.tasks.send_mail.apply_async")
    def test_mail_task_fires(self, send_mail):
        self.test_view_html_toggle()
        response = self.client.post(
            reverse("delete_account"),
            data={
                "reason": "The theme is ugly",
                "confirmed_deletion": "Are you sure?"
            }
        )
        send_mail.assert_called_with(
            kwargs={
                "context": {"reason": "The theme is ugly"},
                "mail_type": "delete_account",
                "objects_to_fetch": [{
                    "app_label": "authentication_service",
                    "model": "coreuser",
                    "id": self.user.id,
                    "context_key": "user"}]
            }
        )
