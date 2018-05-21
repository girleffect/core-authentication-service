from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class TemporaryMigrationUserStore(models.Model):
    username = models.CharField(
        "username",
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    pw_hash = models.CharField("password", max_length=128)
    app_id = models.IntegerField()
    user_id = models.IntegerField()
    site_id = models.IntegerField()

    class Meta:
        unique_together = (
            ("username", "site_id", "app_id"),
            ("user_id", "site_id", "app_id")
        )
        indexes = [
            models.Index(fields=["username", "app_id", "site_id"]),
        ]

    def check_password(self, raw_password):
        return check_password(raw_password, self.pw_hash)

    def set_password(self, raw_password):
        self.pw_hash = make_password(raw_password)
        self.save()
