from django.contrib.auth.backends import ModelBackend


class GirlEffectAuthBackend(ModelBackend):

    def user_can_authenticate(self, user):
        """The default ModelBackend checks if a user is active here and returns
        to the authenticate() method. This however causes the authentication to
        fail and thus show the 'invalid_login' message, instead of the
        'inactive' message that would otherwise be shown. So we override the
        method to always return True and allow the is_active flag to be checked
        on the AuthenticationForm, and to allow the AuthenticationForm to set
        the 'inactive' error message that would otherwise never be reached.
        """
        return True
