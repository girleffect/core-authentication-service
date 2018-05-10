from  django.contrib.auth.base_user import AbstractBaseUser
from  django.contrib.auth.models import UserManager
from django.db import models



class DummyModel(models.Model):
    pass


# TODO Port these over to auth service itself, once all data has been
# finalised. Also point tests and auth backend to correct model when ready.
class TemporaryUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, **extra_fields)


class TemporaryUserStore(AbstractBaseUser):
    # TODO needs client/app ids to filter on.
    USERNAME_FIELD = 'username'
    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        "email address", blank=True, default="", unique=True
    )
    objects = TemporaryUserManager()
