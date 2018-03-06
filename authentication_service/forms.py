import itertools
import logging
from datetime import date  # Required because we patch it in the tests (test_forms.py)
from dateutil.relativedelta import relativedelta

from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import get_user_model, hashers
from django.contrib.auth.forms import (
    UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import BaseFormSet, BaseModelFormSet
from django.forms import modelformset_factory
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _

from authentication_service import models, tasks
from authentication_service.models import UserSecurityQuestion
from authentication_service.utils import update_form_fields
from authentication_service.constants import SECURITY_QUESTION_COUNT, \
    MIN_NON_HIGH_PASSWORD_LENGTH


LOGGER = logging.getLogger(__name__)

# Groupings of form fields which can be used to simplify specifying sets of required fields.
REQUIREMENT_DEFINITION = {
    "names": ["username", "first_name", "last_name", "nickname"],
    "picture": ["avatar"]
}


# Groupings of form fields which can be used to simplify specifying sets of hidden fields.
HIDDEN_DEFINITION = {
    "end-user": ["first_name", "last_name", "country", "gender", "avatar"]
}


class RegistrationForm(UserCreationForm):
    error_css_class = "error"
    required_css_class = "required"
    # Helper field that user's who don't know their birth date can use instead.
    age = forms.IntegerField(min_value=1, max_value=100, required=False)
    # The birth_date is required on the model, but not on the form since it can be indirectly
    # populated if the age is provided.
    birth_date = forms.DateField(widget=AdminDateWidget(attrs={"required": False}), required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "gender", "birth_date", "age",
            "country", "avatar"
        ]

    def __init__(self, security=None, required=None, hidden=None, *args, **kwargs):
        # Super needed before we can actually update the form.
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # Security value is required later in form processes as well.
        self.security = security

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
                        "help_text": ""
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

        # Update the actual fields and widgets.
        update_form_fields(
            self,
            fields_data=fields_data,
            required=required_fields,
            hidden=hidden_fields
        )

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
        if not len(password2) >= MIN_NON_HIGH_PASSWORD_LENGTH:
            raise forms.ValidationError(
                _("Password not long enough.")
            )
        return password2

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

        # Check that either the email or the MSISDN or both is supplied.
        email = cleaned_data.get("email")
        msisdn = cleaned_data.get("msisdn")

        if not email and not msisdn:
            raise ValidationError(_("Enter either email or msisdn"))

        # Check that either the birth date or age is provided. If the birth date is provided, we
        # use it, else we calculate the birth date from the age.
        birth_date = cleaned_data.get("birth_date")
        if not birth_date:
            age = cleaned_data.get("age")
            if age:
                cleaned_data["birth_date"] = date.today() - relativedelta(years=age)
            else:
                raise ValidationError(_("Enter either birth date or age"))

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
            "querstion_queryset", None
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
        email = self.data.get("email", None)

        questions = []
        for form in self.forms:
            # Enforce question selection if no email was provided.
            if not email:
                if not form.cleaned_data.get("question", None):
                    raise ValidationError(
                        _("Please fill in all Security Question fields.")
                    )

            # Ensure unique questions are used.
            question = form.cleaned_data.get("question", None)
            if question in questions and question is not None:
                raise forms.ValidationError(
                    _("Each question can only be picked once.")
                )
            questions.append(question)

        # If not all questions are selected (i.e. has a value other than None),
        # but some have been, raise an error.
        if not all(questions) and any(questions):
            raise ValidationError(
                _("Please fill in all Security Question fields.")
            )


class SecurityQuestionForm(forms.ModelForm):
    question = forms.ModelChoiceField(
        queryset=QuerySet(),
        empty_label="Select a question"
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
    extra=SECURITY_QUESTION_COUNT
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

    class Meta:
        model = get_user_model()
        fields = [
            "first_name", "last_name", "nickname", "email", "msisdn", "gender",
            "birth_date", "country", "avatar"
        ]


class ResetPasswordForm(PasswordResetForm):
    error_css_class = "error"
    required_css_class = "required"

    email = forms.CharField(
        label="Username/email"
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
        self.questions = kwargs.pop("questions")
        super(
            ResetPasswordSecurityQuestionsForm, self).__init__(*args, **kwargs)

        for question in self.questions:
            self.fields["question_%s" % question.id] = forms.CharField(
                label=question.question
            )

    def clean(self):
        for question in self.questions:
            if not self.cleaned_data["question_%s" % question.id]:
                raise ValidationError(_("Please enter your answer."))


class DeleteAccountForm(forms.Form):
    reason = forms.CharField(
        required=False,
        label=_("Please tell use why you want your account deleted")
    )


class SetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        # Super needed before we can actually update the form.
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)
        if not self.user.organisational_unit:
            # Remove default help text, added by password validation,
            # middleware.
            fields_data = {
                "new_password1": {
                    "attributes": {
                        "help_text": ""
                    }
                }
            }
            # Update the actual fields and widgets.
            update_form_fields(
                self,
                fields_data=fields_data,
            )

    def clean_new_password2(self):
        # Short circuit normal validation if not high security.
        if self.user.organisational_unit:
            return super(SetPasswordForm, self).clean_new_password2()

        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        if not len(password2) >= MIN_NON_HIGH_PASSWORD_LENGTH:
            raise forms.ValidationError(
                _("Password not long enough.")
            )
        return password2


# NOTE: SetPasswordForm, is the auth service one. Not django auth as imported
# at top.
# django.contrib.auth.forms.PasswordChangeForm, subclasses
# django.contrib.auth.forms.SetPasswordForm.
class PasswordChangeForm(SetPasswordForm, PasswordChangeForm):
    pass
