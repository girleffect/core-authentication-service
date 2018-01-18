import uuid

from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


GENDER_CHOICES = (
    ("female", "Female"),
    ("male", "Male"),
    ("other", "Other")
)


# NOTE: Changing AUTH_USER_MODEL will cause migration 0001 from otp_totp to
# break once migrations have already been run once.
class CoreUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    email_verified = models.BooleanField(default=False)
    nickname = models.CharField(blank=True, null=True, max_length=30)
    msisdn = models.CharField(blank=True, null=True, max_length=16)
    msisdn_verified = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10, blank=True, null=True, choices=GENDER_CHOICES
    )
    birth_date = models.DateField(blank=True, null=True)
    country = models.ForeignKey("Country", blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True)
    is_employee = models.BooleanField(default=False)
    is_system_user = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class Country(models.Model):
    code = models.CharField(blank=True, null=True, max_length=2)
    name = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return "%s - %s" % (self.code, self.name)


class UserSecurityQuestion(models.Model):
    user = models.ForeignKey("CoreUser")
    answer = models.TextField()
    language_code = models.CharField(max_length=7, choices=settings.LANGUAGES)
    question = models.ForeignKey("SecurityQuestion")

    # NOTE as always, be aware certain update, create and save paths will never
    # trigger save() or the post/pre save signals.
    def save(self, *args, **kwargs):
        # Make use of django built in password hasher, gives us
        # "check_password" method for comparison later on. In short, salts and
        # hashes the text.
        self.answer = hashers.make_password(self.answer.strip().lower())
        super(UserSecurityQuestion, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.language_code, self.question.id)


class SecurityQuestion(models.Model):
    question_text = models.TextField(help_text="Default question text")

    def __str__(self):
        return self.question_text


class QuestionLanguageText(models.Model):
    language_code = models.CharField(max_length=7, choices=settings.LANGUAGES)
    question = models.ForeignKey(
        "SecurityQuestion", on_delete=models.CASCADE
    )
    question_text = models.TextField()

    def validate_unique(self, *args, **kwargs):
        super(QuestionLanguageText, self).validate_unique(*args, **kwargs)
        if SecurityQuestion.objects.filter(
                questionlanguagetext__id=self.id).count() > 1:
            raise ValidationError(
                "Question text can not be assigned to more than one question."
            )

    def __str__(self):
        return "%s - %s" % (self.language_code, self.question.id)
