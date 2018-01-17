from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from core_authentication_service.models import SecurityQuestion, \
    UserSecurityQuestion


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
            ["core_authentication_service/registration/registration_django.html",
            "core_authentication_service/registration/registration.html"]
        )
        self.assertContains(response, "Girl Effect using django admin theme")

        response = self.client.get(reverse("registration") + "?theme=ge")
        self.assertListEqual(
            response.template_name,
            ["core_authentication_service/registration/registration_ge.html",
            "core_authentication_service/registration/registration.html"]
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
                "email": "email@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/test-redirect-url/")

        # Test redirect url, 2fa
        response = self.client.post(
            reverse("registration") + "?show2fa=true&redirect_url=/test-redirect-url/",
            {
                "username": "Username2",
                "password1": "password",
                "password2": "password",
                "email": "email@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/two-factor-auth/account/two_factor/setup/")

        # Test redirect url, high security
        response = self.client.post(
            reverse("registration") + "?security=high&redirect_url=/test-redirect-url/",
            {
                "username": "Username3",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "email": "email@email.com",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/two-factor-auth/account/two_factor/setup/")

    def test_user_save(self):
        response = self.client.post(
            reverse("registration") + "?security=high",
            {
                "username": "Unique@User@Name",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
                "email": "emailunique@email.com",
                "msisdn": "0856545698",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
            }
        )
        self.assertIn(response.url, "/two-factor-auth/account/two_factor/setup/")
        user = get_user_model().objects.get(username="Unique@User@Name")
        self.assertEquals(user.email, "emailunique@email.com")
        self.assertEquals(user.msisdn, "0856545698")

    def test_security_questions_save(self):
        response = self.client.post(
            reverse("registration") + "?security=high",
            {
                "username": "Unique@User@Name",
                "password1": "awesom#saFe3",
                "password2": "awesom#saFe3",
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
        self.assertIn(response.url, "/two-factor-auth/account/two_factor/setup/")
        user = get_user_model().objects.get(username="Unique@User@Name")
        self.assertEquals(user.email, "emailunique@email.com")
        self.assertEquals(user.msisdn, "0856545698")
        question_one = UserSecurityQuestion.objects.get(
            answer="Answer1", question=self.question_one, language_code="en"
        )
        self.assertEquals(question_one.user, user)
        question_two = UserSecurityQuestion.objects.get(
            answer="Answer2", question=self.question_two, language_code="en"
        )
        self.assertEquals(question_two.user, user)

    def test_redirect_view(self):
        # Test without redirect cookie set.
        response = self.client.get(reverse("redirect_view"))
        self.assertIn(response.url, "/two-factor-auth/account/login/")

        # Test with redirect cookie set.
        self.client.cookies.load({"register_redirect": "/test-redirect-after2fa/"})
        response = self.client.get(reverse("redirect_view"))
        self.assertIn(response.url, "/test-redirect-after2fa/")
