from django.utils.translation import ugettext_lazy as _


# Dictionary key within which we should store all our extra session data. Makes
# cleanup much easier as we only need to remove one key. utils.update and get
# data methods already make use of this.
EXTRA_SESSION_KEY = "ge_session_extra_data"


class SessionKeys:
    CLIENT_URI = "ge_oidc_client_uri"
    CLIENT_NAME = "ge_oidc_client_name"
    CLIENT_TERMS = "ge_oidc_client_terms"
    CLIENT_WEBSITE = "ge_oidc_client_website_url"
    # Key is used to store client.id NOT client.client_id
    CLIENT_ID = "ge_oidc_client_id"
    THEME = "theme"

SECURITY_QUESTION_COUNT = 2

MIN_NON_HIGH_PASSWORD_LENGTH = 4

GE_TERMS_URL = "https://www.girleffect.org/terms-and-conditions/"

THEME_NAME_MAP = {
    "springster": "Springster"
}


def get_theme_client_name(request):
    theme = request.META.get("X-Django-Layer", None)
    fallback_name = request.session.get(
        EXTRA_SESSION_KEY,
        {}
    ).get(SessionKeys.CLIENT_NAME)
    return THEME_NAME_MAP.get(theme, fallback_name)


CONSENT_AGE = 13


# Registration Page
# =================

USERNAME_HELP_TEXT = _(
    'It’s important to stay safe and protect your identity online - '
    'so please don’t put your real name or contact details into your '
    'Username. But don’t worry! When you leave comments on the site '
    'you will have the choice to show your username or stay anonymous.'
    '(150 characters or fewer. Letters, digits and @/./+/-/_ only.)')


USERNAME_VALIDATION_ERRORS = {
    'unique': _('Oh no! Looks like somebody else already took your username. '
                'Please try something else, you get to choose an even '
                'cooler one this time!'),
}

FIRST_NAME_HELP_TEXT = _('Please enter your first name')

LAST_NAME_HELP_TEXT = _('Please enter your last name')

EMAIL_LABEL = _('Email address')

EMAIL_HELP_TEXT = _('Please enter your email address')

MOBILE_NUMBER_LABEL = _('Mobile')

MOBILE_NUMBER_HELP_TEXT = _('Please enter your mobile number')

GENDER_HELP_TEXT = _('We promise not to show this publicly')

AGE_HELP_TEXT = _('To join you have to tell us your age. '
                  'Please use numbers only. We’ll keep this info private')

AGE_VALIDATION_ERRORS = {
    'min_age': _('We are sorry, users under the age of {} cannot create an account.'
                 .format(CONSENT_AGE))
}

PASSWORD_LABEL = _('Password')

PASSWORD_HELP_TEXT = _('Make sure your password is super secure! '
                       'A mix of letters and numbers is best.')

PASSWORD_VALIDATION_ERRORS = {
    'password_mismatch': _('The two password fields don\'t match. Please try again.'),
    'complexity': _('Eeek - that password is too short! '
                    'Please create a password that has at least 8 characters and is a '
                    'combination of letters and numbers.')
}

PASSWORD_CONFIRM_LABEL = _('Repeat your password')

PASSWORD_CONFIRM_HELP_TEXT = _('Double check that this password matches the one that you wrote above.')

PASSWORD_CONFIRM_VALIDATION_ERRORS = {
    'password_mismatch': _('The two password fields don\'t match. Please try again.')
}

TERMS_LABEL = _('I accept the Terms and Conditions')

TERMS_HELP_TEXT = _('Our terms & conditions are here to keep you safe! '
                    'Please read them carefully and then tick the box to show you accept them.')

SECURITY_QUESTIONS_QUESTION_LABEL = _("Question")

SECURITY_QUESTIONS_QUESTION_VALIDATION_ERRORS = {
    'required': _("Please fill in all Security Question fields."),
    'unique': _('Oops! You’ve already chosen this question. Please choose a different one.'),
}

SECURITY_QUESTIONS_EMPTY_LABEL = _("Select a question")

SECURITY_QUESTIONS_QUESTION_HELP_TEXT = _('Please choose a security question from the list')

SECURITY_QUESTIONS_ANSWER_LABEL = _('Your Answer')

SECURITY_QUESTIONS_ANSWER_HELP_TEXT = _('Please provide answer to your security question')

SECURITY_QUESTIONS_ANSWER_VALIDATION_ERRORS = {
    'required': _('Don’t forget to answer your question!'),
}


# Login Page
# ==========

LOGIN_USERNAME_LABEL = _('Username')

LOGIN_USERNAME_HELP_TEXT = _('Enter your username')

LOGIN_PASSWORD_LABEL = _('Password')

LOGIN_PASSWORD_HELP_TEXT = _('Enter your password')

LOGIN_VALIDATION_ERRORS = {
    'validation': _('Hmmm this doesn’t look right. '
                    'Check that you’ve entered your username and '
                    'password correctly and try again!')
}


# Update Profile Page
# ===================

UPDATE_VALIDATION_ERRORS = {
    'non_field_errors': _('Oops - there\'s a problem with that info. '
                          'No worries - check out the messages below and we can fix this')
}

PASSWORD_UPDATE_HELP_TEXT = _('Enter your new password')

PASSWORD_UPDATE_VALIDATION_ERRORS = {
    'complexity': _('The password must contain at least 8 characters and needs to be a mix of letters, '
                    'numbers and special characters. '
                    'To make your password safe you must use at least one uppercase and one lowercase letter, '
                    'as well as at least one digit and one special character. '
                    'You should not use personal information or anything too easy to guess')
}

PASSWORD_CONFIRM_UPDATE_LABEL = _('New Password Confirmation')

PASSWORD_CONFIRM_UPDATE_HELP_TEXT = _('Repeat your new password')

PASSWORD_CONFIRM_UPDATE_VALIDATION_ERRORS = {
    'mismatch': _('The two password fields don\'t match')
}


# Delete Acc
# ==========

REASON_LABEL = _('Please tell us why you want your account deleted')
REASON_HELP_TEXT = _('Please enter your response in the provided box')


# Password Recovery
# =================

USERNAME_PASSWORD_RECOVERY_LABEL = _('Username/email')
USERNAME_PASSWORD_RECOVERY_HELP_TEXT = _('Please enter your username to retrieve your password')
USERNAME_PASSWORD_RECOVERY_VALIDATION_ERRORS = {
    'required': _('Please enter your username.')
}
