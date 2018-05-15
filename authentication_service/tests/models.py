from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.contrib.auth.hashers import check_password, make_password



class DummyModel(models.Model):
    pass


class TemporaryUserStore(models.Model):
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
    pw_hash = models.CharField("password", max_length=128)
    app_id = models.IntegerField()
    user_id = models.IntegerField()
    site_id = models.IntegerField()

    def check_password(self, raw_password):
        return check_password(raw_password, self.pw_hash)

    def set_password(self, raw_password):
        self.pw_hash = make_password(raw_password)
        self.save()
