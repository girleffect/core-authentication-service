import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import BaseFormSet
from django.forms import formset_factory
from django.utils.functional import cached_property

from core_authentication_service import models
from core_authentication_service.utils import update_form_fields


LOGGER = logging.getLogger(__name__)


REQUIREMENT_DEFINITION = {
    "names": ["username", "first_name", "last_name", "nickname"],
    "picture": ["avatar"]
}

SECURITY_QUESTION_COUNT = 2

class RegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = [
            "username", "first_name", "last_name", "email",
            "nickname", "msisdn", "birth_date", "country", "avatar"
        ]

    def __init__(self, security=None, required=[],*args, **kwargs):
        # Security value is required later in form processes as well.
        self.security = security

        # Super needed before we can actually update the form.
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # Set update form update variables, for manipulation as init
        # progresses.
        required_fields = []
        fields_data = {}
        if required:
            for field in required:
                required_fields += REQUIREMENT_DEFINITION.get(field, [field])

        # Security level needs some additions before the form is rendered.
        if self.security == "high":
            required_fields += ["email"]
        else:
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
            while required_fields.count(field) > 0:
                required_fields.remove(field)

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
        self.instance.username = self.cleaned_data.get('username')

        # NOTE: Min length might need to be defined somewhere easier to change.
        # Setting doesn't feel 100% right though.
        if not len(password1) > 3 and not len(password2) > 3:
            raise forms.ValidationError(
                "Password not long enough."
            )
        return password2

    def clean(self):
        email = self.cleaned_data.get("email")
        msisdn = self.cleaned_data.get("msisdn")

        if not email and not msisdn:
            raise ValidationError("Enter either email or msisdn")

        return super(RegistrationForm, self).clean()


class SecurityQuestionFormSetClass(BaseFormSet):
    def __init__(self, language, *args, **kwargs):
        self.language = language
        super(SecurityQuestionFormSetClass, self).__init__(*args, **kwargs)

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
        # Save some time, if we already have errors, just return without doing
        # extra work.
        if all(self.errors):
            return

        # This is the email as found on RegistrationForm.
        email = self.data.get("email", None)

        # Enforce question selection if no email was provided.
        if not email:
            for form in self.forms:
                if not form.cleaned_data.get("question", None):
                    raise ValidationError(
                        "Please fill in all Security Question fields"
                    )

        # Ensure unique questions are used.
        questions = []
        for form in self.forms:
            question = form.cleaned_data["question"]
            if question in questions:
                raise forms.ValidationError(
                    "Each question can only be answered once."
                )
            questions.append(question)


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
            choice = list(choice)
            if isinstance(choice[0], int):
                text = questions.get(
                    id=choice[0]).questionlanguagetext_set.filter(
                    language_code=language).first()

                # If there is not language specific text available, default to
                # original.
                choice[1] = text.question_text if text else choice[1]
            updated_choices.append(tuple(choice))

        # Replace choices with new set.
        self.fields["question"].widget.choices = updated_choices


SecurityQuestionFormSet = formset_factory(
    SecurityQuestionForm,
    formset=SecurityQuestionFormSetClass,
    extra=SECURITY_QUESTION_COUNT
)
