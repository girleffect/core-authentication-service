from dateutil.relativedelta import relativedelta
import datetime

from unittest import mock

from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.test import TestCase, override_settings

from authentication_service.forms import (
    RegistrationForm, SecurityQuestionFormSet,
    EditProfileForm, SetPasswordForm, PasswordChangeForm
)
from authentication_service import constants
from authentication_service.models import SecurityQuestion, Organisation
from authentication_service.user_migration.forms import (
    UserDataForm
)


@override_settings(
    HIDE_FIELDS={"global_enable": False,
    "global_fields": ["email", "msisdn", "birth_date"]}
)
class TestRegistrationForm(TestCase):
    maxDiff = None

    def test_default_state(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "terms": ["This field is required."],
            "__all__": ["Enter either email or msisdn", "Enter either birth date or age"]
        })

    def test_default_password_validation(self):
        # Test both required
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "password1": "password",
            "terms": True,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["This field is required."],
        })

        # Test both must match
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
            "password1": "password",
            "password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
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
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
            "password1": "1234",
            "password2": "1234"
        })
        self.assertTrue(form.is_valid())
        form.clean()  # We need to clean the form to ensure birth_date is set appropriately

    def test_default_email_msisdn(self):
        # Test either is required
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
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
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
        })
        self.assertTrue(form.is_valid())

        # Test valid with msisdn
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "msisdn": "0856545698",
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
        })
        self.assertTrue(form.is_valid())

        # Test valid with both
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "email": "email@email.com",
            "msisdn": "0856545698",
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
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
            "country": ["This field is required."],
            "avatar": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "terms": ["This field is required."],
            "__all__": ["Enter either email or msisdn", "Enter either birth date or age"]
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
            "terms": ["This field is required."],
            "__all__": ["Enter either email or msisdn", "Enter either birth date or age"]
        })

    def test_high_security_default_state(self):
        form = RegistrationForm(data={}, security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "terms": ["This field is required."],
            "__all__": ["Enter either email or msisdn", "Enter either birth date or age"]
        })

    def test_high_security_password_validation(self):
        # Test both required
        form = RegistrationForm(data={
            "username": "Username",
            "birth_date": datetime.date(2000, 1, 1),
            "email": "email@email.com",
            "password1": "password",
            "terms": True,
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
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
            "password1": "password",
            "password2": "password2"
        },
            security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length, unique validation and contains more than numeric
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2001, 1, 1),
            "terms": True,
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
            ]
        })

        # Test unique validation
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
            "password1": "asdasdasd",
            "password2": "asdasdasd"
        },
            security="high")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "password2": [
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test close to username
        form = RegistrationForm(data={
            "username": "asdasd",
            "email": "email@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
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
            ]
        })

        # Test success
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date(2001, 1, 1),
            "terms": True,
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        },
            security="high")
        self.assertTrue(form.is_valid())

    def test_age_to_birth_date(self):
        # Test age specified instead of birth_date. Refer to the link below for an explanation of
        # why the mocking is done the way it is:
        # http://www.voidspace.org.uk/python/mock/examples.html#partial-mocking
        with mock.patch("authentication_service.forms.date") as mocked_date:
            mocked_date.today.return_value = datetime.date(2000, 1, 2)
            mocked_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

            form = RegistrationForm(
                data={
                    "username": "Username",
                    "email": "email@email.com",
                    "age": "16",
                    "terms": True,
                    "password1": "asdasdasdA@1",
                    "password2": "asdasdasdA@1"
                },
                security="high"
            )
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data["birth_date"], datetime.date(1984, 1, 2))

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
            "country": ["This field is required."],
            "avatar": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "terms": ["This field is required."],
            "__all__": ["Enter either email or msisdn", "Enter either birth date or age"]
        })

    def test_email_validation(self):
        user = get_user_model().objects.create_user(
            username="awesomeuser",
            email="awesome@email.com",
            password="Awesome!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        user.save()
        form = RegistrationForm(data={
            "username": "Username",
            "email": "awesome@email.com",
            "birth_date": datetime.date(2000, 1, 1),
            "terms": True,
            "password1": "password",
            "password2": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "email": ["Core user with this Email address already exists."],
        })

        # Test users without emails do not cause validation errors.
        user = get_user_model().objects.create_user(
            username="awesomeuser2",
            password="Awesome!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        user.save()
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "msisdn": "0856545698",
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
        })
        self.assertTrue(form.is_valid())
        form = RegistrationForm(data={
            "username": "Username2",
            "password1": "password",
            "password2": "password",
            "msisdn": "0856545698",
            "terms": True,
            "birth_date": datetime.date(2000, 1, 1)
        })
        self.assertTrue(form.is_valid())

    def test_min_required_age_dob(self):
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "birth_date": datetime.date.today() - relativedelta(years=10),
            "terms": True,
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        })
        self.assertFalse(form.is_valid())

    def test_min_required_age(self):
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "age": constants.CONSENT_AGE-1,
            "terms": True,
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "age": [
                "We are sorry, " \
                f"users under the age of {constants.CONSENT_AGE}" \
                " cannot create an account."
            ]
        })
        with mock.patch("authentication_service.forms.date") as mocked_date:
            mocked_date.today.return_value = datetime.date(2018, 1, 2)
            mocked_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
            form = RegistrationForm(data={
                "username": "Username",
                "email": "email@email.com",
                "birth_date": datetime.date(2018-constants.CONSENT_AGE, 1, 3),
                "terms": True,
                "password1": "asdasdasdA@1",
                "password2": "asdasdasdA@1"
            })
            self.assertFalse(form.is_valid())
            form = RegistrationForm(data={
                "username": "Username",
                "email": "email@email.com",
                "birth_date": datetime.date(2018-constants.CONSENT_AGE+1, 1, 3),
                "terms": True,
                "password1": "asdasdasdA@1",
                "password2": "asdasdasdA@1"
            })
            self.assertFalse(form.is_valid())

    def test_on_required_age(self):
        form = RegistrationForm(data={
            "username": "Username",
            "email": "email@email.com",
            "age": constants.CONSENT_AGE,
            "terms": True,
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        })
        self.assertTrue(form.is_valid())
        with mock.patch("authentication_service.forms.date") as mocked_date:
            mocked_date.today.return_value = datetime.date(2018, 1, 2)
            mocked_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
            form = RegistrationForm(data={
                "username": "Username",
                "email": "email@email.com",
                "birth_date": datetime.date(2018-constants.CONSENT_AGE, 1, 2),
                "terms": True,
                "password1": "asdasdasdA@1",
                "password2": "asdasdasdA@1"
            })
            self.assertTrue(form.is_valid())

    def test_unique_username(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            birth_date=datetime.date(2000, 1, 1),
            email="wrong@email.com",
            gender="female",
            email_verified=True
        )
        form = RegistrationForm(data={
            "username": user.username,
            "email": "email@email.com",
            "age": constants.CONSENT_AGE,
            "terms": True,
            "password1": "asdasdasdA@1",
            "password2": "asdasdasdA@1"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": [
                "Oh no! Looks like somebody else already took your username. "
                "Please try something else, you get to choose an even cooler one this time!"
            ],
        })


class TestRegistrationFormHTML(TestCase):
    maxDiff = None

    def test_default_state(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        # TODO Update once end user has new copy
        self.assertNotIn("<li>Your password can&#39;t be too similar to your " \
        "other personal information.</li><li>Your password must contain at " \
        "least 8 characters.</li><li>Your password can&#39;t be a commonly " \
        "used password.</li><li>Your password can&#39;t be entirely numeric." \
        "</li><li>The password must contain at least one uppercase letter, " \
        "one lowercase one, a digit and special character.</li>", form.as_div())

    def test_high_security_state(self):
        form = RegistrationForm(data={}, security="high")
        self.assertFalse(form.is_valid())
        self.assertIn("<li>Your password can&#39;t be too similar to your " \
        "other personal information.</li><li>Your password must contain at " \
        "least 8 characters.</li><li>Your password can&#39;t be a commonly " \
        "used password.</li><li>Your password can&#39;t be entirely numeric." \
        "</li><li>The password must contain at least one uppercase letter, " \
        "one lowercase one, a digit and special character.</li>", form.as_div())


class TestRegistrationFormWithHideSetting(TestCase):
    maxDiff = None

    def test_default_state(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
            "gender": ["This field is required."],
            "age": ["This field is required."],
            "terms": ["This field is required."],
        })

    def test_default_settings(self):
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "gender": "none",
            "age": "16",
            "terms": True,
        })
        self.assertTrue(form.is_valid())

        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "gender": "female",
            "age": "16",
            "terms": True,
        })
        self.assertTrue(form.is_valid())

        # Test valid with email
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "email": "email@email.com",
            "gender": "female",
            "age": "16",
            "terms": True,
        })
        self.assertTrue(form.is_valid())

        # Test valid with msisdn
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "msisdn": "0856545698",
            "gender": "female",
            "age": "16",
            "terms": True,
        })
        self.assertTrue(form.is_valid())

        # Test valid with both
        form = RegistrationForm(data={
            "username": "Username",
            "password1": "password",
            "password2": "password",
            "email": "email@email.com",
            "msisdn": "0856545698",
            "birth_date": datetime.date(2000, 1, 1),
            "gender": "female",
            "age": "16",
            "terms": True,
        })
        self.assertTrue(form.is_valid())


class TestSecurityQuestionFormSet(TestCase):
    maxDiff = None

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
        self.assertEqual(
            formset.non_form_errors(),
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
        self.assertEqual(
            formset.errors, [
                {"answer": ["Don’t forget to answer your question!"]},
                {"answer": ["Don’t forget to answer your question!"]}
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
        self.assertEqual(
            formset.non_form_errors(),
            ["Oops! You’ve already chosen this question. Please choose a different one."]
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
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            birth_date=datetime.date(2000, 1, 1),
            email="wrong@email.com",
            gender="female",
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
            "msisdn": "+27821234567",
            "age": 34,
            "gender": "female"
        }

        form = EditProfileForm(instance=self.user, data=data)
        self.assertTrue(form.has_changed())
        self.assertTrue(form.is_valid())
        form.save()

        user = get_user_model().objects.get(username=self.user.username)
        self.assertNotEqual(datetime.date(2000, 1, 1), user.birth_date)
        self.assertEqual(data["email"], user.email)
        self.assertEqual(data["msisdn"], user.msisdn)

    def test_nothing_updated(self):
        data = model_to_dict(self.user)

        form = EditProfileForm(instance=self.user, data=data)
        self.assertFalse(form.has_changed())
        self.assertTrue(form.is_valid())

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

    def test_min_required_age_dob(self):
        form = EditProfileForm(data={
            "birth_date": datetime.date.today() - relativedelta(years=10),
        })
        self.assertFalse(form.is_valid())

    @override_settings(
        HIDE_FIELDS={"global_enable": False,
        "global_fields": ["birth_date"]}
    )
    def test_age_and_dob_required(self):
        form = EditProfileForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "__all__": [
                "Enter either birth date or age"
            ],
            "gender": ["This field is required."],
        })

    def test_min_required_age(self):
        form = EditProfileForm(data={
            "age": constants.CONSENT_AGE-1,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "gender": ["This field is required."],
            "age": [
                "We are sorry, " \
                f"users under the age of {constants.CONSENT_AGE}" \
                " cannot create an account."
            ]
        })
        with mock.patch("authentication_service.forms.date") as mocked_date:
            mocked_date.today.return_value = datetime.date(2018, 1, 2)
            mocked_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
            form = EditProfileForm(data={
                "birth_date": datetime.date(2018-constants.CONSENT_AGE, 1, 3),
            })
            self.assertFalse(form.is_valid())
            form = EditProfileForm(data={
                "birth_date": datetime.date(2018-constants.CONSENT_AGE+1, 1, 3),
            })
            self.assertFalse(form.is_valid())

    def test_on_required_age(self):
        form = EditProfileForm(data={
            "age": constants.CONSENT_AGE,
            "gender": "female"
        })
        self.assertTrue(form.is_valid())
        with mock.patch("authentication_service.forms.date") as mocked_date:
            mocked_date.today.return_value = datetime.date(2018, 1, 2)
            mocked_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
            form = EditProfileForm(data={
                "birth_date": datetime.date(2018-constants.CONSENT_AGE, 1, 2),
                "gender": "female"
            })
            self.assertTrue(form.is_valid())


class TestPasswordResetForm(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="forgotmypassword",
            birth_date=datetime.date(2000, 1, 1),
            email="atleastihavethis@email.com",
            email_verified=True
        )
        cls.user.save()
        org = Organisation.objects.create(
            name="uniquename",
            description="some text"
        )
        cls.org_user = get_user_model().objects.create_user(
            username="org_forgotmypassword",
            birth_date=datetime.date(2000, 1, 1),
            email="org_atleastihavethis@email.com",
            email_verified=True,
            organisation=org
        )
        cls.org_user.save()

    def test_none_org_html_state(self):
        form = SetPasswordForm(self.user)
        html = form.as_div()
        self.assertNotIn(
            "The password must contain at least one uppercase letter, one lowercase one, a digit and special character",
            html
        )

    def test_org_html_state(self):
        form = SetPasswordForm(self.org_user)
        html = form.as_div()
        self.assertIn(
            "The password must contain at least one uppercase letter, one lowercase one, a digit and special character",
            html
        )

    def test_user_password_validation(self):
        # Test both required
        form = SetPasswordForm(self.user, data={
            "new_password1": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["This field is required."],
        })

        # Test both must match
        form = SetPasswordForm(self.user, data={
            "new_password1": "password",
            "new_password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length
        form = SetPasswordForm(self.user, data={
            "new_password1": "123",
            "new_password2": "123"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "Eeek - that password is too short! "
                "Please create a password that has at least 8 characters and is a combination of letters and numbers."
            ]
        })

    def test_org_user_password_validation(self):
        # Test both required
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["This field is required."],
        })

        # Test both must match
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "password",
            "new_password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length, unique validation and contains more than numeric
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "123",
            "new_password2": "123"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "This password is too short. It must contain at least 8 characters.",
                "This password is entirely numeric.",
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test unique validation
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "asdasdasd",
            "new_password2": "asdasdasd"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test close to username
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "forgotmypass",
            "new_password2": "forgotmypass"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "The password is too similar to the username.",
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test success
        form = SetPasswordForm(self.org_user, data={
            "new_password1": "asdasdasdA@1",
            "new_password2": "asdasdasdA@1"
        })
        self.assertTrue(form.is_valid())


class TestPasswordChangeForm(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="forgotmypassword",
            birth_date=datetime.date(2000, 1, 1),
            email="atleastihavethis@email.com",
            email_verified=True
        )
        cls.user.set_password("atleast_its_not_1234")
        cls.user.save()
        org = Organisation.objects.create(
            name="uniquename",
            description="some text"
        )
        cls.org_user = get_user_model().objects.create_user(
            username="org_forgotmypassword",
            birth_date=datetime.date(2000, 1, 1),
            email="org_atleastihavethis@email.com",
            email_verified=True,
            organisation=org
        )
        cls.org_user.set_password("atleast_its_not_1234")
        cls.org_user.save()

    def test_none_org_html_state(self):
        form = PasswordChangeForm(self.user)
        html = form.as_div()
        self.assertIn(
            "Enter your new password",
            html
        )

    def test_org_html_state(self):
        form = PasswordChangeForm(self.org_user)
        html = form.as_div()
        self.assertIn(
            "Enter your new password",
            html
        )

    def test_user_password_validation(self):
        # Test both required
        form = PasswordChangeForm(self.user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["This field is required."],
        })

        # Test both must match
        form = PasswordChangeForm(self.user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "password",
            "new_password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length
        form = PasswordChangeForm(self.user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "123",
            "new_password2": "123"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "Eeek - that password is too short! "
                "Please create a password that has at least 8 characters and is a combination of letters and numbers."
            ]
        })

    def test_org_user_password_validation(self):
        # Test both required
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "password",
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["This field is required."],
        })

        # Test both must match
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "password",
            "new_password2": "password2"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": ["The two password fields don't match. Please try again."],
        })

        # Test min length, unique validation and contains more than numeric
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "123",
            "new_password2": "123"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "This password is too short. It must contain at least 8 characters.",
                "This password is entirely numeric.",
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test unique validation
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "asdasdasd",
            "new_password2": "asdasdasd"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test close to username
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "forgotmypass",
            "new_password2": "forgotmypass"
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            "new_password2": [
                "The password is too similar to the username.",
                "The password must contain at least one uppercase letter, "
                "one lowercase one, a digit and special character."
            ]
        })

        # Test success
        form = PasswordChangeForm(self.org_user, data={
            "old_password": "atleast_its_not_1234",
            "new_password1": "asdasdasdA@1",
            "new_password2": "asdasdasdA@1"
        })
        self.assertTrue(form.is_valid())


class TestRequiredDecorator(TestCase):
    maxDiff = None

    def test_registration(self):
        form = RegistrationForm()
        html = form.as_div()
        for name, field in form.fields.items():
            # Terms is not rendered as part of the form html method
            if field.required and name is not "terms":
                self.assertIn("*", field.label)
                self.assertIn(
                    field.label,
                    html
                )

    def test_edit_profile(self):
        user = get_user_model().objects.create_user(
            username="requiredlabeluser",
            email="awesome@email.com",
            password="Awesome!234",
            birth_date=datetime.date(2001, 1, 1)
        )
        form = EditProfileForm(instance=user)
        html = form.as_div()
        for name, field in form.fields.items():
            if field.required:
                self.assertIn("*", field.label)
                self.assertIn(field.label, html)

    def test_user_migration(self):
        form = UserDataForm()
        html = form.as_div()
        for name, field in form.fields.items():
            if field.required:
                self.assertIn("*", field.label)
                self.assertIn(field.label, html)
