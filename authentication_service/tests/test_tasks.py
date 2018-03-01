import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authentication_service import tasks


# TODO we need more tests function tests, for now the two use cases are covered.
class SendMailCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="leaving_task_user", email="awol@id.com",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.set_password("atleast_its_not_1234")
        cls.user.save()

    def test_account_deletion_mail(self):
        tasks.send_mail(
            {"reason": "The theme is ugly"},
            "delete_account",
            objects_to_fetch=[{
                "app_label": "authentication_service",
                "model": "coreuser",
                "id": self.user.id,
                "context_key": "user"
            }]
        )
        self.assertEqual(
            mail.outbox[0].to, tasks.MAILS["default"]["recipients"]
        )
        self.assertEqual(
            mail.outbox[0].subject,
            tasks.MAILS["delete_account"]["subject"]
        )
        self.assertEqual(mail.outbox[0].body,
            "The following user would "\
            "like to delete their Girl Effect account."\
            "\nusername: %s"
            "\nemail: %s"\
            "\nmsisdn: %s"\
            "\nreason :The theme is ugly\n" %(
                self.user.username,
                self.user.email,
                self.user.msisdn
            )
        )

    def test_reset_password_mail(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        context = {
            "email": self.user.email,
            "domain": "test:8000",
            "site_name": "test_site",
            "uid": uid,
            "token": token,
            "protocol": "http",
        }
        extra = {"recipients": [self.user.email]}
        user = {
            "app_label": self.user._meta.app_label,
            "model": self.user._meta.model_name,
            "id": self.user.id,
            "context_key": "user",
        }
        context["uid"] = context["uid"].decode("utf-8")
        tasks.send_mail(
             context,
            "password_reset",
            objects_to_fetch=[user],
            extra=extra
        )
        self.assertEqual(
            mail.outbox[0].to,
            [self.user.email]
        )
        self.assertEqual(
            mail.outbox[0].subject,
            tasks.MAILS["password_reset"]["subject"]
        )
        self.assertEqual(mail.outbox[0].body,
            "\nYou're receiving this email because you requested a password "\
            "reset for your user account at test_site.\n\nPlease go to the "\
            "following page and choose a new password:\n\n"\
            "http://test:8000/reset/"\
            "%s/"\
            "%s/\n\n"\
            "Your username, in case you've forgotten: %s\n\n"\
            "Thanks for using our site!\n\nThe test_site team\n\n\n" % (
                context["uid"],
                token,
                self.user.username,
            )
        )
