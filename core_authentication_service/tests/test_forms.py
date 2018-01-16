from django.test import TestCase

from core_authentication_service.forms import RegistrationForm
from core_authentication_service.models import SecurityQuestion


class TestRegistrationForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestRegistrationForm, cls).setUpTestData()

        # Security questions
        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )

    def test_default_state(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "__all__": ["Enter either email or msisdn"]
        })

    def test_default_password_validation(self):

        # Test both required
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["This field is required."],
        })

        # Test both must match
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "password",
            "password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["The two password fields didn't match."],
        })

        # Test min length
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "123",
            "password2": "123"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["Password not long enough."],
        })

        # Test passwords happy
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "1234",
            "password2": "1234"
        })
        self.assertTrue(form.is_valid())

    def test_default_email_msisdn(self):

        # Test either is requried
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "__all__": ["Enter either email or msisdn"]
        })

        # Test valid with email
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "email": "email@email.com",
        })
        self.assertTrue(form.is_valid())

        # Test valid with msisdn
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "msisdn": "0856545698",
        })
        self.assertTrue(form.is_valid())

        # Test valid with both
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "email": "email@email.com",
            "msisdn": "0856545698",
        })
        self.assertTrue(form.is_valid())

    def test_default_required_toggle(self):
        required = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "gender", "birth_date", "country", "avatar"
        ]
        form = RegistrationForm(data={}, required=required)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "email": ["This field is required."],
            "nickname": ["This field is required."],
            "msisdn": ["This field is required."],
            "gender": ["This field is required."],
            "birth_date": ["This field is required."],
            "country": ["This field is required."],
            "avatar": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "__all__": ["Enter either email or msisdn"]
        })

    def test_default_required_toggle_mapping(self):
        required = [
            "names", "picture"
        ]
        form = RegistrationForm(data={}, required=required)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
            "nickname": ["This field is required."],
            "avatar": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "__all__": ["Enter either email or msisdn"]
        })

    def test_hight_security_default_state(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "__all__": ["Enter either email or msisdn"]
        })
