from django.contrib.auth.hashers import check_password, make_password
from django.contrib.postgres.fields import JSONField
from django.db import models

from oidc_provider.models import Client


class TemporaryMigrationUserStore(models.Model):
    username = models.CharField(
        "username",
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    pw_hash = models.CharField("password", max_length=128)
    user_id = models.IntegerField()
    client = models.ForeignKey(Client, to_field="client_id", null=True)
    question_one = JSONField(blank=True, default={})
    question_two = JSONField(blank=True, default={})
    answer_one = models.CharField(max_length=128, null=True, blank=True)
    answer_two = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = (
            ("username", "client"),
            ("user_id", "client")
        )
        indexes = [
            models.Index(fields=["username", "client"]),
        ]

    def get_hash_value(self, value):
        """
        Convenience method, a central space where hashed values for this
        instance can be controller if needed.
        """
        return make_password(value)

    def check_password(self, raw_password):
        return check_password(raw_password, self.pw_hash)

    def check_answer_one(self, answer):
        return check_password(answer.strip().lower(), self.answer_one)

    def check_answer_two(self, answer):
        return check_password(answer.strip().lower(), self.answer_two)

    def set_password(self, raw_password):
        self.pw_hash = self.get_hash_value(raw_password)
        self.save()

    def set_answers(self, answer_one=None, answer_two=None):
        if answer_one:
            self.answer_one = self.get_hash_value(answer_one.strip().lower())
        if answer_two:
            self.answer_two = self.get_hash_value(answer_two.strip().lower())
        self.save()
