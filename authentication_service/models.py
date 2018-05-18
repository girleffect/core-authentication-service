import uuid

from partial_index import PartialIndex

from django.conf import settings
from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


GENDER_CHOICES = (
    ("female", _("Female")),
    ("male", _("Male")),
    ("other", _("Other"))
)


class AutoQueryField(models.TextField):
    """
    Custom field to populate concatenated query field.

    Should work for more scenarios than just save() or create()
    """
    def __init__(self, query_fields=None, *args, **kwargs):
        self.query_fields = query_fields or []
        super(AutoQueryField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = " ".join(
            getattr(
                model_instance, field, "") or "" for field in self.query_fields
        )

        # Default will be an empty string. DB value will be the default set to
        # the field or the value after data migration.
        if value != "":
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(AutoQueryField, self).pre_save(model_instance, add)


class TrigramIndex(GinIndex):
    """
    Inspired by solution on:
    https://stackoverflow.com/questions/44820345/

    Should perform a sql action similar to:
    CREATE INDEX trgm_idx ON <table>_<column> USING gin (<column> gin_trgm_ops);
    """
    def get_sql_create_template_values(self, model, schema_editor, using):
        sql_values = super(TrigramIndex, self).get_sql_create_template_values(
            model, schema_editor, using)

        # Replace existing column values with gin_trgm_ops appended ones.
        columns = sql_values["columns"].split(", ")
        new_columns = []
        for column in columns:
            new_columns.append(f"{column} gin_trgm_ops")
        sql_values["columns"] = ", ".join(new_columns)
        return sql_values


# NOTE: Changing AUTH_USER_MODEL will cause migration 0001 from otp_totp to
# break once migrations have already been run once.
class CoreUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    email = models.EmailField(
        _("email address"), blank=True, null=True, unique=True)
    email_verified = models.BooleanField(default=False)
    nickname = models.CharField(blank=True, null=True, max_length=30)
    msisdn = models.CharField(blank=True, null=True, max_length=16)
    msisdn_verified = models.BooleanField(default=False)
    gender = models.CharField(
        _("gender"), max_length=10, blank=True, null=True,
        choices=GENDER_CHOICES
    )
    birth_date = models.DateField()
    country = models.ForeignKey("Country", blank=True, null=True,
        verbose_name=_("country"))
    avatar = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organisational_unit = models.ForeignKey(
        "OrganisationalUnit", blank=True, null=True
    )
    q = AutoQueryField(
        query_fields=[
            "email", "first_name", "last_name", "msisdn", "nickname", "username"
        ],
        null=True
    )
    migration_data = JSONField(blank=True, default={})

    def __init__(self, *args, **kwargs):
        super(CoreUser, self).__init__(*args, **kwargs)
        self._original_email = self.email
        self._original_msisdn = self.msisdn

    def save(self, *args, **kwargs):
        # If email or msisdn has changed, their verified flags need
        # to be updated.
        if self.email != self._original_email:
            self.email_verified = False
        if self.msisdn != self._original_msisdn:
            self.msisdn_verified = False

        # To prevent unique constaint issues that are not db related, if the
        # email is an empty string make it None. A None value on forms gets
        # converted to an empty string somewhere along the line.
        if self.email == "":
            self.email = None
        super(CoreUser, self).save(*args, **kwargs)

    @property
    def has_security_questions(self):
        return self.usersecurityquestion_set.all() or None

    class Meta:
        indexes = [
            models.Index(fields=["date_joined",]),
            models.Index(fields=["gender",]),
            models.Index(fields=["last_login",]),
            models.Index(fields=["updated_at",]),
            PartialIndex(
                fields=["is_active",], unique=False,
                where_postgresql="is_active = false"
            ),
            PartialIndex(
                fields=["email_verified",], unique=False,
                where_postgresql="email_verified = true"
            ),
            PartialIndex(
                fields=["msisdn_verified",], unique=False,
                where_postgresql="msisdn_verified = true"
            ),
            TrigramIndex(fields=["username"],),
            TrigramIndex(fields=["msisdn"],),
            TrigramIndex(fields=["email"],),
            TrigramIndex(fields=["first_name"],),
            TrigramIndex(fields=["last_name"],),
            TrigramIndex(fields=["nickname"],),
            TrigramIndex(fields=["q"],),
        ]


class UserSite(models.Model):
    user = models.ForeignKey("CoreUser")
    site_id = models.IntegerField()
    consented_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "site_id"]
        indexes = [
            models.Index(fields=["site_id"]),
        ]


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        verbose_name_plural = _("Countries")

    def __str__(self):
        return self.name


class UserSecurityQuestion(models.Model):
    user = models.ForeignKey("CoreUser")
    answer = models.TextField(_("answer"))
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
    question_text = models.TextField(help_text=_("Default question text"))

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
                _("Question text can not be assigned to more than one question.")
            )

    def __str__(self):
        return "%s - %s" % (self.language_code, self.question.id)


class OrganisationalUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
