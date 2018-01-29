from django.test import TestCase
from django.contrib.auth import get_user_model, hashers

from authentication_service.models import SecurityQuestion, \
    UserSecurityQuestion


class TestRegistrationModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestRegistrationModels, cls).setUpTestData()
        cls.user = get_user_model().objects.create(
            username="AnswerTest@User@Name",
        )

        # Security questions
        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

    def test_answer_hashing(self):
        text = "Some_text"
        answer = UserSecurityQuestion.objects.create(
            user=self.user,
            answer=text,
            language_code="en",
            question=self.question_one
        )
        self.assertTrue(hashers.check_password(text.lower(), answer.answer))

        text = " Some spacious _text "
        answer = UserSecurityQuestion.objects.create(
            user=self.user,
            answer=text,
            language_code="en",
            question=self.question_one
        )
        text = "Some spacious _text"
        self.assertTrue(hashers.check_password(text.lower(), answer.answer))
