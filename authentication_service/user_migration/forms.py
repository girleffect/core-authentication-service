from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.utils import six
from django.utils.translation import ugettext as _

from authentication_service.user_migration.models import TemporaryMigrationUserStore

# Lifted from Django user model validator.
USERNAME_VALIDATOR = (
    UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
)


class UserDataForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[USERNAME_VALIDATOR],
    )
    age = forms.IntegerField(
        min_value=1,
        max_value=100
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError(
                _("A user with that username already exists.")
            )
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        if len(password2) < 4:
            raise forms.ValidationError(
                _("Password needs to be at least 4 characters long.")
            )
        return password2


class SecurityQuestionGateForm(forms.Form):
    """
    NOTE agreed upon, if user only has one answer, it must be answer_one
    """
    error_css_class = "error"
    required_css_class = "required"
    answer_one = forms.CharField(
        label="",
        max_length=128
    )
    answer_two = forms.CharField(
        label="",
        max_length=128
    )

    def __init__(self, user, language, *args, **kwargs):
        self._user = user
        language = language
        question_one = self._user.question_one[language]
        super(SecurityQuestionGateForm, self).__init__(*args, **kwargs)
        self.fields["answer_one"].label = question_one
        if not self._user.answer_two:
            self.fields["answer_two"].required = False
            self.fields["answer_two"].widget.is_required = False
            self.fields["answer_two"].widget = HiddenInput()
            self.fields["answer_two"].disabled = True
        else:
            question_two = self._user.question_two[language]
            self.fields["answer_two"].label = question_two

    def clean(self):
        cleaned_data = super(SecurityQuestionGateForm, self).clean()
        answer_one = cleaned_data.get("answer_one")
        answer_two = cleaned_data.get("answer_two")

        if not self._user.answer_two:
            if not self._user.check_answer_one(answer_one):
                raise ValidationError(_("Incorrect answer provided"))
        elif not all([
                self._user.check_answer_one(answer_one),
                self._user.check_answer_two(answer_two)]):
            raise ValidationError(_("Incorrect answers provided"))
        return cleaned_data


class PasswordResetForm(forms.Form):
    error_css_class = "error"
    required_css_class = "required"
    password_one = forms.CharField(
        label=_("Password"),
        max_length=128,
        widget=forms.PasswordInput
    )
    password_two = forms.CharField(
        label=_("Confirm password"),
        max_length=128,
        widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_password_two(self):
        password_one = self.cleaned_data.get("password_one")
        password_two = self.cleaned_data.get("password_two")
        if password_one and password_two and password_one != password_two:
            raise forms.ValidationError(
                _("Passwords do not match.")
            )

        if not len(password_two) >= 4:
            raise forms.ValidationError(
                _("Password not long enough.")
            )
        return password_two

    def update_password(self):
        self._user.set_password(self.cleaned_data["password_two"])
