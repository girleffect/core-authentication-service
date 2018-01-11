from django.contrib.auth.models import AbstractUser
from django.db import models


class CoreUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    nickname = models.CharField(blank=True, null=True, max_length=30)
    msisd = models.CharField(blank=True, null=True, max_length=16)
    msisdn_verified = models.BooleanField(default=False)
    gender = models.IntegerField(blank=True, null=True)
    birth_date = models.DateTimeField(blank=True, null=True)
    country_code = models.CharField(blank=True, null=True, max_length=2)
    avatar = models.ImageField(blank=True, null=True)
    is_employee = models.BooleanField(default=False)
    is_system_user = models.BooleanField(default=False)
