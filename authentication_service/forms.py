import itertools
import logging
# Required because we patch it in the tests (test_forms.py)
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.forms.widgets import Textarea
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UsernameField
from django.utils.http import urlsafe_base64_encode
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import (
    UserCreationForm, PasswordResetForm, AuthenticationForm)
from django.contrib.auth.tokens import default_token_generator
from django.forms import BaseModelFormSet, HiddenInput, modelformset_factory
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

from authentication_service import constants
from authentication_service import models, tasks
from authentication_service.fields import ParagraphField
from authentication_service.utils import update_form_fields

from authentication_service.decorators import required_form_fields_label_alter


LOGGER = logging.getLogger(__name__)

# Groupings of form fields which can be used to simplify specifying sets of required fields.
REQUIREMENT_DEFINITION = {
    "names": ["username", "first_name", "last_name", "nickname"],
    "picture": ["avatar"]
}


# Groupings of form fields which can be used to simplify specifying sets of hidden fields.
HIDDEN_DEFINITION = {
    "end-user": ["first_name", "last_name", "country", "msisdn"]
}


class RegistrationForm(UserCreationForm):
    error_css_class = "error"
    required_css_class = "required"
    error_messages = constants.PASSWORD_VALIDATION_ERRORS

    terms = forms.BooleanField(
        label=constants.TERMS_LABEL,
        help_text=constants.TERMS_HELP_TEXT
    )
    username = forms.CharField(
        label=constants.LOGIN_USERNAME_LABEL,
        help_text=constants.USERNAME_HELP_TEXT,
        error_messages=constants.USERNAME_VALIDATION_ERRORS
    )
    # Helper field that user's who don't know their birth date can use instead.
    age = forms.IntegerField(
        min_value=1, max_value=100, required=False,
        help_text=constants.AGE_HELP_TEXT
    )

    class Meta:
        model = get_user_model()
        fields = [
            # Org field should never be directly editable via the form
            "organisation",
            "username", "avatar", "first_name", "last_name", "email",
            "nickname", "msisdn", "gender", "age", "birth_date",
            "country", "password1", "password2"
        ]
        exclude = ["terms"]
        field_classes = {
            "organisation": ParagraphField,
        }

    @required_form_fields_label_alter
    def __init__(self, terms_url=None, security=None, required=None,
            hidden=None, organisation_id=None, *args, **kwargs):
        # Super needed before we can actually update the form.
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.terms_url = terms_url or constants.GE_TERMS_URL

        # Security value is required later in form processes as well.
        self.security = security

        # Organisation field setup and tweaking
        if organisation_id:
            # Oganisation is a special field, it was never meant to be user
            # editable. Disable or alter specific attributes manually.

            # The ModelForm is still passing the queryset to the field, make
            # use of it instead of doing own lookup as well.
            self.organisation = self["organisation"].field.queryset.filter(
                id=organisation_id).first()

            # Replace the existing ParagraphField with a new one that contains
            # a new piece of text to display.
            self["organisation"].field = ParagraphField(
                paragraph="<b>%s</b>" % _(
                    "Organisation user has been invited to:"
                    f" {self.organisation.name}"
                )
            )
        else:
            # Fully remove field if no organisation id was provided
            self.fields.pop("organisation")

        # Set update form update variables, for manipulation as init
        # progresses.
        fields_data = {}
        required = required or []
        required_fields = set(itertools.chain.from_iterable(
            REQUIREMENT_DEFINITION.get(field, [field]) for field in required
        ))

        hidden = hidden or []
        hidden_fields = set(itertools.chain.from_iterable(
            HIDDEN_DEFINITION.get(field, [field]) for field in hidden
        ))

        # Security level needs some additions before the form is rendered.
        if self.security == "high":
            required_fields.add("email")
        else:
            # Remove default help text, added by password validation,
            # middleware.
            fields_data = {
                "password1": {
                    "attributes": {
                        "help_text": password_validation.password_validators_help_text_html()
                        if self.security == 'high' else constants.PASSWORD_HELP_TEXT
                    }
                }
            }

        form_fields = set(self.fields.keys())
        # Handle incorrectly specified required fields
        incorrect_fields = required_fields - form_fields
        for field in incorrect_fields:
            LOGGER.warning(
                "Received required field that is not on form: %s" % field
            )
            required_fields.discard(field)

        # Handle incorrectly specified hidden fields
        incorrect_fields = hidden_fields - form_fields
        for field in incorrect_fields:
            LOGGER.warning(
                "Received hidden field that is not on form: %s" % field
            )
            hidden_fields.discard(field)

        none_html_tag_translatable_terms_anchor_text = _(
            "Click here to view the terms and conditions"
        )
        fields_data.update({
            "birth_date": {
                "attributes": {
                    "help_text": _("Please use dd/mm/yyyy format")
                }
            },
            "terms": {
                "attributes": {
                    "help_text": (
                        f'<div class="Field-message">{constants.TERMS_HELP_TEXT}</div>'
                        f'<a href="{self.terms_url}">'
                        f"{none_html_tag_translatable_terms_anchor_text}</a>"
                    )
                }
            },
            "nickname": {
                "attributes": {
                    "label": constants.NICKNAME_LABEL,
                }
            },
            "msisdn": {
                "attributes": {
                    "label": constants.MOBILE_NUMBER_LABEL,
                    "help_text": constants.MOBILE_NUMBER_HELP_TEXT,
                }
            },
            "age": {
                "attributes": {
                    "label": constants.AGE_LABEL,
                    "help_text": constants.AGE_HELP_TEXT,
                }
            },
            "first_name": {
                "attributes": {
                    "label": constants.FIRST_NAME_LABEL,
                    "help_text": constants.FIRST_NAME_HELP_TEXT,
                }
            },
            "last_name": {
                "attributes": {
                    "label": constants.LAST_NAME_LABEL,
                    "help_text": constants.LAST_NAME_HELP_TEXT,
                }
            },
            "email": {
                "attributes": {
                    "label": constants.EMAIL_LABEL,
                    "help_text": constants.EMAIL_HELP_TEXT,
                }
            },
            "gender": {
                "attributes": {
                    "label": constants.GENDER_LABEL,
                    "help_text": constants.GENDER_HELP_TEXT,
                }
            },
            "password1": {
                "attributes": {
                    "label": constants.PASSWORD_LABEL,
                    "help_text": password_validation.password_validators_help_text_html()
                    if self.security == 'high' else constants.PASSWORD_HELP_TEXT,
                }
            },
            "password2": {
                "attributes": {
                    "label": constants.PASSWORD_CONFIRM_LABEL,
                    "help_text": constants.PASSWORD_CONFIRM_HELP_TEXT,
                }
            },
            "username": {
                "attributes": {
                    "label": constants.LOGIN_USERNAME_LABEL,
                    "help_text": constants.USERNAME_HELP_TEXT,
                    "error_messages": constants.USERNAME_VALIDATION_ERRORS
                }
            }
        })

        # Final overrides from settings
        if settings.HIDE_FIELDS["global_enable"]:
            # Age is not on the model, but is used to calculate the user birth
            # date. Gender is not required on the model but is required for all
            # users.
            required_fields.update(["age", "gender"])

            for field in settings.HIDE_FIELDS["global_fields"]:
                if field in required_fields:
                    continue  # Required field cannot be hidden

                self.fields[field].required = False
                self.fields[field].widget.is_required = False
                hidden_fields.update([field])

        # Update the actual fields and widgets.
        update_form_fields(
            self,
            fields_data=fields_data,
            required=required_fields,
            hidden=hidden_fields
        )

        # Manual overrides:

        # NOTE: These will then also ignore all other overrides set up till
        # this point.

        # The birth_date is required on the model, but not on the form since it
        # can be indirectly populated if the age is provided.
        self.fields["birth_date"].required = False
        self.fields["birth_date"].widget.is_required = False

    def _html_output(self, *args, **kwargs):
        # Django does not allow the exclusion of fields on non-ModelForm forms.

        # Remove the field from the form during the html output creation added
        # to template directly.
        original_fields = self.fields.copy()
        self.fields.pop("terms")
        html = super(RegistrationForm, self)._html_output(*args, **kwargs)

        # Replace the original fields.
        self.fields = original_fields
        return html

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age and age < constants.CONSENT_AGE:
            raise forms.ValidationError(
                constants.AGE_VALIDATION_ERRORS.get('min_age'))

        return age

    # NOTE the order of RegistrationForm.Meta.fields, age is needed before
    # birth_date. If this is not the case, the age value will always be None.
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        age = self.cleaned_data.get("age")
        today = date.today()
        if not birth_date and age:
            birth_date = today - relativedelta(years=age)
        if birth_date:
            diff = relativedelta(today, birth_date)
            if diff.years < constants.CONSENT_AGE:
                raise forms.ValidationError(_(
                    f"We are sorry, users under the age of {constants.CONSENT_AGE}"
                    " cannot create an account."
                ))
        return birth_date

    def clean_password2(self):
        # Short circuit normal validation if not high security.
        if self.security == "high":
            return super(RegistrationForm, self).clean_password2()

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        # NOTE: Min length might need to be defined somewhere easier to change.
        # Setting doesn't feel 100% right though.
        if not len(password2) >= constants.MIN_NON_HIGH_PASSWORD_LENGTH:
            raise forms.ValidationError(
                _("Password not long enough.")
            )
        return password2

    def clean_organisation(self):
        return self.organisation

    def _get_validation_exclusions(self):
        # By default fields that are allowed to be blank on the model are not
        # excluded so as to run unique validation. However it being allowed
        # null is not taken into consideration as None values get converted to
        # an empty string value before reaching to model save level.
        exclude = super(RegistrationForm, self)._get_validation_exclusions()
        if self.cleaned_data.get("email", None) is None:
            exclude.append("email")
        return exclude

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        # Get a new empty ErrorList
        additional_page_errors = self.error_class()

        # Check that either the email or the MSISDN or both is supplied.
        email = cleaned_data.get("email")
        msisdn = cleaned_data.get("msisdn")
        if not email and not msisdn and not \
                settings.HIDE_FIELDS["global_enable"]:
            additional_page_errors.append(ValidationError(
                _("Enter either email or msisdn"))
            )

        # Check that either the birth date or age is provided. If the birth
        # date is provided, we use it, else we calculate the birth date from
        # the age.
        birth_date = cleaned_data.get("birth_date")
        if not set(["age", "birth_date"]) & set(self.errors) and \
                not cleaned_data.get("birth_date") and \
                not cleaned_data.get("age") and \
                not settings.HIDE_FIELDS["global_enable"]:
            additional_page_errors.append(ValidationError(
                _("Enter either birth date or age"))
            )

        # Add new errors to existing error list, allows the raising of all
        # clean method errors at once. Rather than one at a time per post.
        # NOTE: non_field_errors() is most likely still empty. It usually gets
        # populated by raising a ValidationError in clean().
        if additional_page_errors:
            form_level_errors = self.non_field_errors()
            self.errors["__all__"] = form_level_errors + additional_page_errors

        return cleaned_data


class SecurityQuestionFormSetClass(BaseModelFormSet):
    def __init__(self, language, *args, **kwargs):
        # Short circuit default code that causes entire model queryset to be
        # pulled in for any user or anon.

        # Formset model queryset.
        self._queryset = kwargs.pop(
            "queryset", self.model.objects.none()
        )

        # Question field, queryset.
        self.question_queryset = kwargs.pop(
            "question_queryset", None
        )

        # Hook value for wizards
        self.email = kwargs.pop(
            "step_email", None
        )
        self.language = language
        super(SecurityQuestionFormSetClass, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super(SecurityQuestionFormSetClass, self).get_form_kwargs(index)
        kwargs["questions"] = self.get_questions
        kwargs["language"] = self.language
        if self.question_queryset:
            kwargs["question_queryset"] = self.question_queryset
        return kwargs

    @cached_property
    def get_questions(self):
        return models.SecurityQuestion.objects.prefetch_related(
            "questionlanguagetext_set").all()

    def clean(self):
        # This is the email as found on RegistrationForm.
        email = self.data.get("email", self.email)

        questions = []
        for form in self.forms:
            # Enforce question selection if no email was provided.
            if not email:
                if not form.cleaned_data.get("question", None):
                    raise ValidationError(
                        constants.SECURITY_QUESTIONS_QUESTION_VALIDATION_ERRORS.get('required')
                    )

            # Ensure unique questions are used.
            question = form.cleaned_data.get("question", None)
            if question in questions and question is not None:
                raise forms.ValidationError(
                    constants.SECURITY_QUESTIONS_QUESTION_VALIDATION_ERRORS.get('unique')
                )
            questions.append(question)

        # If not all questions are selected (i.e. has a value other than None),
        # but some have been, raise an error.
        if not all(questions) and any(questions):
            raise ValidationError(
                constants.SECURITY_QUESTIONS_QUESTION_VALIDATION_ERRORS.get('required')
            )


class SecurityQuestionForm(forms.ModelForm):
    question = forms.ModelChoiceField(
        queryset=QuerySet(),
        label=constants.SECURITY_QUESTIONS_QUESTION_LABEL,
        empty_label=constants.SECURITY_QUESTIONS_EMPTY_LABEL,
        help_text=constants.SECURITY_QUESTIONS_QUESTION_HELP_TEXT,
    )

    answer = forms.CharField(
        widget=forms.Textarea,
        label=constants.SECURITY_QUESTIONS_ANSWER_LABEL,
        help_text=constants.SECURITY_QUESTIONS_ANSWER_HELP_TEXT,
        error_messages=constants.SECURITY_QUESTIONS_ANSWER_VALIDATION_ERRORS
    )

    class Meta:
        model = models.UserSecurityQuestion
        fields = ["question", "answer"]

    def __init__(self, questions, language, *args, **kwargs):
        super(SecurityQuestionForm, self).__init__(*args, **kwargs)
        self.fields["question"].queryset = questions

        # Always clear out answer fields.
        self.initial["answer"] = ""

        # Choice tuple can't be directly updated. Update only the widget choice
        # text, value is used for validation and saving.
        updated_choices = []
        for choice in self.fields["question"].widget.choices:
            if isinstance(choice[0], int):
                text = questions.get(
                    id=choice[0]).questionlanguagetext_set.filter(
                    language_code=language).first()

                # If there is no language specific text available, default to
                # the original.
                choice = (choice[0], text.question_text if text else choice[1])
            updated_choices.append(tuple(choice))

        # Replace choices with new set.
        self.fields["question"].widget.choices = updated_choices


SecurityQuestionFormSet = modelformset_factory(
    models.UserSecurityQuestion,
    SecurityQuestionForm,
    formset=SecurityQuestionFormSetClass,
    extra=constants.SECURITY_QUESTION_COUNT
)

UpdateSecurityQuestionFormSet = modelformset_factory(
    models.UserSecurityQuestion,
    SecurityQuestionForm,
    formset=SecurityQuestionFormSetClass,
    extra=0
)


class EditProfileForm(forms.ModelForm):
    error_css_class = "error"
    required_css_class = "required"

    # Helper field that user's who don't know their birth date can use instead.
    age = forms.IntegerField(
        min_value=1, max_value=100, required=False,
        label=constants.AGE_LABEL,
        help_text=constants.AGE_HELP_TEXT
    )
    email = forms.EmailField(
        required=False,
        label=constants.EMAIL_LABEL,
        help_text=constants.EMAIL_HELP_TEXT)
    nickname = forms.CharField(
        label=constants,
        required=False, help_text=constants.USERNAME_HELP_TEXT)

    last_name = forms.CharField(
        label=constants.LAST_NAME_LABEL,
        required=False, help_text=constants.LAST_NAME_HELP_TEXT)

    first_name = forms.CharField(
        label=constants.FIRST_NAME_LABEL,
        required=False, help_text=constants.FIRST_NAME_HELP_TEXT)

    msisdn = forms.CharField(
        required=False,
        label=constants.MOBILE_NUMBER_LABEL,
        help_text=constants.MOBILE_NUMBER_HELP_TEXT
    )
    gender = forms.ChoiceField(
        required=False,
        label=constants.GENDER_LABEL,
        choices=models.GENDER_CHOICES,
        # help_text=constants.GENDER_HELP_TEXT,
    )

    class Meta:
        model = get_user_model()
        fields = [
            "first_name", "last_name", "nickname", "email", "msisdn", "gender",
            "age", "birth_date", "country", "avatar"
        ]

    @required_form_fields_label_alter
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        hidden_fields = []
        fields_data= {"birth_date": {
                "attributes": {
                    "help_text": _("Please use dd/mm/yyyy format")
                }
            },
            "age": {
                "attributes": {
                    "label": _("Age")
                }
            }
        }

        # Gender is not required on the model but is required for all users
        required_fields = ["gender"]

        # Final overrides from settings
        if settings.HIDE_FIELDS["global_enable"]:
            for field in settings.HIDE_FIELDS["global_fields"]:
                if field in required_fields:
                    continue  # Required field cannot be hidden

                self.fields[field].required = False
                self.fields[field].widget.is_required = False
                hidden_fields.append(field)

        if self.instance.organisation:
            # Show email address explicitly since it can be hidden in the
            # global hidden fields.
            hidden_fields.remove("email")
        else:
            for field in HIDDEN_DEFINITION["end-user"]:
                hidden_fields.append(field)

        # Init age field
        birth_date = self.instance.birth_date
        if birth_date:
            self.fields["age"].initial = \
                date.today().year - birth_date.year
        # Update the actual fields and widgets.
        update_form_fields(
            self,
            fields_data=fields_data,
            required=required_fields,
            hidden=hidden_fields
        )

        # Manual overrides:

        # NOTE: These will then also ignore all other overrides set up till
        # this point.

        # The birth_date is required on the model, but not on the form since it
        # can be indirectly populated if the age is provided.
        self.fields["birth_date"].required = False
        self.fields["birth_date"].widget.is_required = False

    def _html_output(self, *args, **kwargs):
        # Exclude fields from the html not the form itself. Makes using built
        # in save method easier.

        # Currently birth_date should not be merely hidden, it causes the
        # browser to send back the original value. Birth date is always used
        # for user age over the actual age field.
        if self.fields["birth_date"].required is False \
                and isinstance(self.fields["birth_date"].widget, HiddenInput):
            # Remove the field from the form during the html output creation.
            original_fields = self.fields.copy()
            self.fields.pop("birth_date")
            html = super(EditProfileForm, self)._html_output(*args, **kwargs)

            # Replace the original fields.
            self.fields = original_fields
            return html
        return super(EditProfileForm, self)._html_output(*args, **kwargs)

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age and age < constants.CONSENT_AGE:
            raise forms.ValidationError(_(
                f"We are sorry, users under the age of {constants.CONSENT_AGE}"
                " cannot create an account."
            ))
        return self.cleaned_data.get("age")

    # NOTE the order of EditProfileForm.Meta.fields, age is needed before
    # birth_date. If this is not the case, the age value will always be None.
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        age = self.cleaned_data.get("age")
        today = date.today()
        if not birth_date and age:
            birth_date = today - relativedelta(years=age)
        if birth_date:
            diff = relativedelta(today, birth_date)
            if diff.years < constants.CONSENT_AGE:
                raise forms.ValidationError(_(
                    f"We are sorry, users under the age of {constants.CONSENT_AGE}"
                    " cannot create an account."
                ))
        return birth_date

    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()

        # Get a new empty ErrorList
        additional_page_errors = self.error_class()

        # Check that either the birth date or age is provided. If the birth
        # date is provided, we use it, else we calculate the birth date from
        # the age.
        birth_date = cleaned_data.get("birth_date")
        if not set(["age", "birth_date"]) & set(self.errors) and \
                not cleaned_data.get("birth_date") and \
                not cleaned_data.get("age") and \
                not settings.HIDE_FIELDS["global_enable"]:
            additional_page_errors.append(ValidationError(
                _("Enter either birth date or age"))
            )

        # Add new errors to existing error list, allows the raising of all
        # clean method errors at once. Rather than one at a time per post.
        # NOTE: non_field_errors() is most likely still empty. It usually gets
        # populated by raising a ValidationError in clean().
        if additional_page_errors:
            form_level_errors = self.non_field_errors()
            self.errors["__all__"] = form_level_errors + additional_page_errors

        return cleaned_data


class ResetPasswordForm(PasswordResetForm):
    error_css_class = "error"
    required_css_class = "required"

    email = forms.CharField(
        label=_("Username/email")
    )

    def clean(self):
        identifier = self.cleaned_data.get("email")
        if not identifier:
            raise ValidationError(
                _("Please enter your username or email address.")
            )

    # TODO Refactor. Seems like parts might not be needed.
    def save(self, domain_override=None,
             subject_template_name="registration/password_reset_subject.txt",
             email_template_name="registration/password_reset_email.html",
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            user = context.pop("user")
            extra = {"recipients": [user.email]}
            user = {
                "app_label": user._meta.app_label,
                "model": user._meta.model_name,
                "id": user.id,
                "context_key": "user",
            }
            context["uid"] = context["uid"].decode("utf-8")
            tasks.send_mail.apply_async(
                kwargs={
                    "context": context,
                    "mail_type": "password_reset",
                    "objects_to_fetch": [user],
                    "extra": extra
                }
            )


class ResetPasswordSecurityQuestionsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.questions = kwargs.pop("questions", [])
        super(
            ResetPasswordSecurityQuestionsForm, self).__init__(*args, **kwargs)

        for question in self.questions:
            self.fields["question_%s" % question.id] = forms.CharField(
                label=question.question
            )

    def clean(self):
        for question in self.questions:
            if not self.cleaned_data.get("question_%s" % question.id, None):
                raise ValidationError(
                    _("Please answer all your security questions.")
                )


class DeleteAccountForm(forms.Form):
    reason = forms.CharField(
        required=False,
        label=_("Please tell us why you want your account deleted"),
        widget=Textarea()
    )


class SetPasswordForm(DjangoSetPasswordForm):
    """
    Change password validation requirements based on current user.

    Users with an organisation assigned to them have a high likelihood
    of also obtaining roles. As such they require the default password
    validation middleware functionality.

    Users without an organisation assigned will not have roles assigned
    to them. They also do not need to adhere to the full validation suite, only
    a limited subset.
    """
    error_messages = constants.PASSWORD_VALIDATION_ERRORS
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label=constants.PASSWORD_CONFIRM_UPDATE_LABEL,
        help_text=constants.PASSWORD_CONFIRM_UPDATE_HELP_TEXT
    )

    def __init__(self, user, *args, **kwargs):
        # Super needed before we can actually update the form.
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)
        if self.user and not self.user.organisation:
            # Remove default help text, added by password validation,
            # middleware.
            fields_data = {
                "new_password1": {
                    "attributes": {
                        "help_text": constants.PASSWORD_UPDATE_HELP_TEXT
                    }
                }
            }
            # Update the actual fields and widgets.
            update_form_fields(
                self,
                fields_data=fields_data,
            )

    def clean_new_password2(self):
        # If user has an organisation, let original validation kick in.
        if self.user.organisation:
            return super(SetPasswordForm, self).clean_new_password2()

        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        if not len(password2) >= constants.MIN_NON_HIGH_PASSWORD_LENGTH:
            raise forms.ValidationError(
                self.error_messages['password_min_length'])
        return password2


class PasswordChangeForm(SetPasswordForm, DjangoPasswordChangeForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label=constants.PASSWORD_LABEL,
        help_text=constants.PASSWORD_UPDATE_HELP_TEXT
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label=constants.PASSWORD_CONFIRM_LABEL,
        help_text=constants.PASSWORD_CONFIRM_UPDATE_HELP_TEXT
    )


class LoginForm(AuthenticationForm):
    error_messages = constants.LOGIN_VALIDATION_ERRORS

    username = UsernameField(
        max_length=254,
        label=constants.LOGIN_USERNAME_LABEL,
        error_messages=constants.LOGIN_USERNAME_VALIDATION_ERRORS,
        help_text=constants.LOGIN_USERNAME_HELP_TEXT,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        strip=False,
        label=constants.LOGIN_PASSWORD_LABEL,
        help_text=constants.LOGIN_PASSWORD_HELP_TEXT,
        widget=forms.PasswordInput,
    )
