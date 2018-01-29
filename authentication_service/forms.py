import itertools
import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import BaseFormSet
from django.forms import formset_factory
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _

from authentication_service import models
from authentication_service.utils import update_form_fields
from authentication_service.constants import SECURITY_QUESTION_COUNT, \
    MIN_NON_HIGH_PASSWORD_LENGTH


LOGGER = logging.getLogger(__name__)


REQUIREMENT_DEFINITION = {
    "names": ["username", "first_name", "last_name", "nickname"],
    "picture": ["avatar"]
}


class RegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "gender", "birth_date", "country", "avatar"
        ]

    def __init__(self, security=None, required=None, *args, **kwargs):
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

        incorrect_fields = set(required_fields) - set(self.fields.keys())
        for field in incorrect_fields:
            LOGGER.warning(
                "Received field to alter that is not on form: %s" % field
            )
            required_fields.discard(field)

        # Update the actual fields and widgets.
        update_form_fields(
            self,
            fields_data=fields_data,
            required=required_fields
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

    def clean(self):
        email = self.cleaned_data.get("email")
        msisdn = self.cleaned_data.get("msisdn")

        if not email and not msisdn:
            raise ValidationError(_("Enter either email or msisdn"))

        return super(RegistrationForm, self).clean()


class SecurityQuestionFormSetClass(BaseFormSet):
    def __init__(self, language, *args, **kwargs):
        super(SecurityQuestionFormSetClass, self).__init__(*args, **kwargs)
        self.language = language

    def get_form_kwargs(self, index):
        kwargs = super(SecurityQuestionFormSetClass, self).get_form_kwargs(index)
        kwargs["questions"] = self.get_questions
        kwargs["language"] = self.language
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


class SecurityQuestionForm(forms.Form):
    question = forms.ModelChoiceField(
        queryset=QuerySet(),
        empty_label="Select a question"
    )
    answer = forms.CharField()

    def __init__(self, questions, language, *args, **kwargs):
        super(SecurityQuestionForm, self).__init__(*args, **kwargs)
        self.fields["question"].queryset = questions

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


SecurityQuestionFormSet = formset_factory(
    SecurityQuestionForm,
    formset=SecurityQuestionFormSetClass,
    extra=SECURITY_QUESTION_COUNT
)
