import string

from django.utils.translation import ugettext
from django.core.exceptions import ValidationError
from authentication_service.constants import PASSWORD_VALIDATION_ERRORS


class DiversityValidator(object):
    """
    Validate whether the password has uppercase, lowercase, digits and special characters.
    """

    def validate(self, password, user=None):
        charsets = [
            set(string.ascii_lowercase),
            set(string.ascii_uppercase),
            set(string.digits),
            set(string.punctuation)
        ]
        password_chars = set(password)

        # Check that the password characters comes from all charsets.
        valid = all(password_chars.intersection(charset) for charset in charsets)
        if not valid:
            raise ValidationError(
                PASSWORD_VALIDATION_ERRORS.get('complexity'),
                code='password_not_diverse',
            )

    def get_help_text(self):
        return ugettext(
            "The password must contain at least one uppercase "
            "letter, one lowercase one, a digit and special character.",
        )
