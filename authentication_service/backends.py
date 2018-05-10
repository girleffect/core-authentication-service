from django.contrib.auth.backends import ModelBackend

#from authentication_service.models import TemporaryUserStore
from authentication_service.tests.models import TemporaryUserStore


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


class MigratedUserAuthBackend(ModelBackend):
    """
    django ModelBackend, with a tweaked authenticate method.
    Checks another table for users explicitly.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):

        # TODO use ?client_id grabbed from request.GET.get("next")
        try:
            user = TemporaryUserStore.objects.get(username=username)
        except TemporaryUserStore.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            TemporaryUserStore().set_password(password)
        else:
            if user.check_password(password):
                return user
