from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class TemporaryMigrationUserStore(models.Model):
    username = models.CharField(
        "username",
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    pw_hash = models.CharField("password", max_length=128)
    user_id = models.IntegerField()
    client_id = models.IntegerField()
    question_one = models.CharField(max_length=128)
    question_two = models.CharField(max_length=128)
    answer_one = models.CharField(max_length=128)
    answer_two = models.CharField(max_length=128)

    class Meta:
        unique_together = (
            ("username", "client_id"),
            ("user_id", "client_id")
        )
        indexes = [
            models.Index(fields=["username", "client_id"]),
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
