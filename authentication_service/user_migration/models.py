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
    answer_one = models.CharField(max_length=128)
    answer_two = models.CharField(max_length=128)

    class Meta:
        unique_together = (
            ("username", "client"),
            ("user_id", "client")
        )
        indexes = [
            models.Index(fields=["username", "client"]),
        ]

    def check_password(self, raw_password):
        return check_password(raw_password, self.pw_hash)

    def check_answers(self, answer_one, answer_two):
        return all([
            check_password(answer_one, self.answer_one),
            check_password(answer_two, self.answer_two)
        ])

    def set_password(self, raw_password):
        self.pw_hash = make_password(raw_password)
        self.save()

    def set_anwers(self, raw_password):
        self.answer_one = make_password(answer_one)
        self.answer_two = make_password(answer_two)
        self.save()
