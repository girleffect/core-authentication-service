from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from core_authentication_service.models import SecurityQuestion


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
