from django.contrib.auth import get_user_model
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase
from django.http import QueryDict

from authentication_service.forms import RegistrationForm, \
    SecurityQuestionForm, SecurityQuestionFormSet, EditProfileForm
from authentication_service.models import SecurityQuestion


class TestRegistrationForm(TestCase):

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

    def test_high_security_default_state(self):
        form = RegistrationForm(data={}, security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "__all__": ["Enter either email or msisdn"]
        })

    def test_high_security_password_validation(self):

        # Test both required
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "password",
        },
        security="high")
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
        },
        security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["The two password fields didn't match."],
        })

        # Test min length, unique validation and contains more than numeric
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "123",
            "password2": "123"
        },
        security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
        "password2": [
            "This password is too short. It must contain at least 8 characters.",
            "This password is entirely numeric.",
            "The password must contain at least one uppercase letter, "
            "one lowercase one, a digit and special character."
        ]})


        # Test unique validation
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "asdasdasd",
            "password2": "asdasdasd"
        },
        security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
        "password2": [
            "The password must contain at least one uppercase letter, "
            "one lowercase one, a digit and special character."
        ]})

        # Test close to username
        form = RegistrationForm(data={
            "username": "asdasd",
            "email": "email@email.com",
            "password1": "asdasdasd",
            "password2": "asdasdasd"
        },
        security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
        "password2": [
            "The password is too similar to the username.",
            "The password must contain at least one uppercase letter, "
            "one lowercase one, a digit and special character."
        ]})

        # Test success
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        },
        security="high")
        self.assertTrue(form.is_valid())

    def test_high_security_required_toggle(self):
        required = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "gender", "birth_date", "country", "avatar"
        ]
        form = RegistrationForm(data={}, security="high", required=required)
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


class TestSecurityQuestionForm(TestCase):

    def test_default_state(self):
        form = SecurityQuestionForm(
            data={},
            questions=SecurityQuestion.objects.all(),
            language="en"
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "question": ["This field is required."],
            "answer": ["This field is required."],
        })


class TestSecurityQuestionFormSet(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestSecurityQuestionFormSet, cls).setUpTestData()

        # Security questions
        cls.question_one = SecurityQuestion.objects.create(
            question_text="Some text for the one question"
        )
        cls.question_two = SecurityQuestion.objects.create(
            question_text="Some text for the other question"
        )


    def test_default_state(self):
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": "",
            "form-0-answer": "",
            "form-1-question": "",
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(),
            ["Please fill in all Security Question fields."]
        )

    def test_validation(self):
        # Ensure that all questions need to be answered when email is not
        # present.
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": "",
            "form-0-answer": "",
            "form-1-question": "",
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(),
            ["Please fill in all Security Question fields."]
        )

        # Ensure its valid if email is present
        data = {
            "email": "email@email.com",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": "",
            "form-0-answer": "",
            "form-1-question": "",
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertTrue(formset.is_valid())

        # Ensure that all questions need to be answered. If anything was filled
        # in on the questions.
        data = {
            "email": "email@email.com",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": self.question_one.id,
            "form-0-answer": "",
            "form-1-question": "",
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(),
            ["Please fill in all Security Question fields."]
        )
        data = {
            "email": "email@email.com",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": "",
            "form-0-answer": "",
            "form-1-question": self.question_two.id,
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(),
            ["Please fill in all Security Question fields."]
        )

        # Test answer validation
        data = {
            "email": "email@email.com",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": self.question_one.id,
            "form-0-answer": "",
            "form-1-question": self.question_two.id,
            "form-1-answer": ""
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors,
            [
                {"answer": ["This field is required."]},
                {"answer": ["This field is required."]}
            ]
        )

        # Test same questions can't be selected more than once.
        data = {
            "email": "",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": self.question_one.id,
            "form-0-answer": "Answer1",
            "form-1-question": self.question_one.id,
            "form-1-answer": "Answer2"
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(),
            ["Each question can only be picked once."]
        )

        # Test valid with email.
        data = {
            "email": "email@email.com",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": self.question_one.id,
            "form-0-answer": "Answer1",
            "form-1-question": self.question_two.id,
            "form-1-answer": "Answer2"
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertTrue(formset.is_valid())

        # Test valid without email.
        data = {
            "email": "",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-question": self.question_one.id,
            "form-0-answer": "Answer1",
            "form-1-question": self.question_two.id,
            "form-1-answer": "Answer2"
        }
        formset = SecurityQuestionFormSet(data=data, language="en")
        self.assertTrue(formset.is_valid())


class EditProfileFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="wrong@email.com",
            email_verified=True
        )
        cls.user.save()

    def test_default_state(self):
        form = EditProfileForm(instance=self.user)

        initial_dict = {
            "email": "wrong@email.com"
        }

        # Check initial values
        self.assertTrue(
            set(initial_dict.items()).issubset(set(form.initial.items())))

    def test_update_profile(self):
        data = {
            "email": "right@email.com",
            "msisdn": "+27821234567"
        }

        form = EditProfileForm(instance=self.user, data=data)

        self.assertTrue(form.is_valid())

    def test_nothing_updated(self):
        data = {}

        form = EditProfileForm(instance=self.user, data=data)

        self.assertTrue(form.is_valid())
        self.assertTrue(self.user.email_verified)

    def test_invalid_form(self):
        data = {
            "email": "not_an_email",
            "gender": "no",
            "country": "abc"
        }

        form = EditProfileForm(instance=self.user, data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {
                "email":
                    ["Enter a valid email address."],
                "gender":
                    ["Select a valid choice. no is not one of the available "
                     "choices."],
                "country":
                    ["Select a valid choice. That choice is not one of the "
                     "available choices."],
            }
        )
