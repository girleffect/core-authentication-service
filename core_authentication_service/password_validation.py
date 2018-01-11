import string

from django.utils.translation import ugettext
from django.core.exceptions import ValidationError


class DiversityValidator(object):
    """
    Validate whether the password has uppercase, lowercase, digits and special characters.
    """

    def validate(self, password, user=None):
        valid = all([
            len(set(string.ascii_lowercase).intersection(password)) > 0,
            len(set(string.ascii_uppercase).intersection(password)) > 0,
            len(set(string.digits).intersection(password)) > 0,
            len(set(string.punctuation).intersection(password)) > 0
        ])
        if not valid:
            raise ValidationError(
                ugettext(
                    "This password must container at least one uppercase "\
                    "letter, one lowercase one, a digit and special character.",
                ),
                code='password_not_diverse',
            )

    def get_help_text(self):
        return ugettext(
            "This password must container at least one uppercase "\
            "letter, one lowercase one, a digit and special character.",
        )
