import datetime
import logging
import uuid
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.management import call_command
from django.test import override_settings, TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from oidc_provider.models import Token, UserConsent, Code

from access_control import Invitation
from authentication_service import tasks, models

# TODO we need more test functions, for now only actual use cases are covered.
from authentication_service.models import Organisation, UserSite, UserSecurityQuestion


class SendMailCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="leaving_task_user", email="awol@id.com",
            birth_date=datetime.date(2001, 1, 1)
        )
        cls.user.set_password("atleast_its_not_1234")
        cls.user.save()

    def test_no_recipient(self):
        test_output = "ERROR:authentication_service.tasks:Attempted to send an email of " \
                      "type 'unknown' without recipients"
        with self.assertLogs(level=logging.ERROR) as cm:
            tasks.send_mail(
                {"a": "b"},
                "unknown"
            )
        output = cm.output
        self.assertIn(test_output, output[0])
        self.assertEqual(len(mail.outbox), 0)

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
            mail.outbox[0].to, tasks.MAIL_TYPE_DATA["delete_account"]["recipients"]
        )
        self.assertEqual(
            mail.outbox[0].subject,
            tasks.MAIL_TYPE_DATA["delete_account"]["subject"]
        )
        self.assertEqual(mail.outbox[0].body,
            "The following user would "\
            "like to delete their Girl Effect account."\
            "\nid: %s"
            "\nusername: %s"
            "\nemail: %s"\
            "\nmsisdn: %s"\
            "\nreason: The theme is ugly\n" % (
                self.user.id,
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
            tasks.MAIL_TYPE_DATA["password_reset"]["subject"]
        )
        self.assertEqual(mail.outbox[0].body,
            "\nYou're receiving this email because you requested a password "\
            "reset for your user account at test_site.\n\nPlease go to the "\
            "following page and choose a new password:\n\n"\
            "http://test:8000/en/reset/"\
            "%s/"\
            "%s/\n\n"\
            "Your username, in case you've forgotten: %s\n\n"\
            "Thanks for using our site!\n\nThe test_site team\n\n\n" % (
                context["uid"],
                token,
                self.user.username,
            )
        )


class SendInvitationMail(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.organisation = Organisation.objects.create(
            id=1,
            name="test unit",
            description="Description"
        )

        cls.user = get_user_model().objects.create(
            username="test_user_1",
            first_name="Firstname",
            last_name="Lastname",
            email="firstname@example.com",
            is_superuser=1,
            is_staff=1,
            birth_date=datetime.date(2000, 1, 1)
        )

    def test_send_invitation_mail(self):
        test_invitation_id = uuid.uuid4()
        invitation = Invitation(
            id=test_invitation_id.hex,
            invitor_id=self.user.id,
            first_name="Thename",
            last_name="Thesurname",
            email="thename.thesurname@example.com",
            organisation_id=self.organisation.id,
            expires_at=timezone.now() + datetime.timedelta(minutes=10),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        with self.assertLogs(level=logging.INFO) as cm:
            tasks.send_invitation_email(invitation.to_dict(), "http://test.me/register")

        self.assertEquals(len(mail.outbox), 1)

        # Check part of the email
        self.assertIn("Dear Thename Thesurname", mail.outbox[0].body)

        # Check log line
        self.assertEqual(cm.output[0], "INFO:authentication_service.tasks:Sent invitation from "
                                       "test_user_1 to Thename Thesurname")


class PurgeExpiredInvitations(TestCase):

    @override_settings(AC_OPERATIONAL_API=MagicMock(
        purge_expired_invitations=MagicMock(return_value={
            "amount": 4
        }))
    )
    def test_purge_expired_invitation_task(self):
        result = tasks.purge_expired_invitations(
            cutoff_date=str(datetime.datetime.now().date())
        )
        self.assertEqual(result["amount"], 4)


class DeleteUserAndData(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.organisation = Organisation.objects.create(
            id=1,
            name="test unit",
            description="Description"
        )

        cls.deleter = user_model.objects.create(
            username="deleter",
            first_name="Del",
            last_name="Eter",
            email="deleter@example.com",
            is_superuser=False,
            is_staff=False,
            birth_date=datetime.date(2000, 1, 1)
        )

        cls.user = user_model.objects.create(
            username="Username",
            first_name="Us",
            last_name="Er",
            email="user@example.com",
            is_superuser=False,
            is_staff=False,
            birth_date=datetime.date(2000, 1, 1)
        )

        cls.user_site = models.UserSite.objects.create(
            user=cls.user,
            site_id=1
        )
        cls.user_site.save()

        call_command("load_security_questions")

        cls.user_security_question = models.UserSecurityQuestion.objects.create(
            user=cls.user,
            question_id=1
        )

    @override_settings(
        AC_OPERATIONAL_API=MagicMock(
            delete_user_data=MagicMock(return_value={"amount": 10})
        ),
        USER_DATA_STORE_API=MagicMock(
            deleteduser_read=MagicMock(return_value=None),
            deleteduser_create=MagicMock(return_value={}),
            deleteduser_update=MagicMock(return_value={}),
            deletedusersite_read=MagicMock(return_value=None),
            deletedusersite_create=MagicMock(return_value={}),
            deletedusersite_update=MagicMock(return_value={}),
            delete_user_data=MagicMock(return_value={"amount": 5})
        )
    )
    def test_delete_user_and_data_task(self):
        with self.assertLogs(level=logging.DEBUG) as logger:
            tasks.delete_user_and_data_task(
                user_id=self.user.id,
                deleter_id=self.deleter.id,
                reason="Because this is a test"
            )

        self.assertEquals(
            logger.output, [
                "DEBUG:authentication_service.tasks:10 rows deleted from Access Control",
                "DEBUG:authentication_service.tasks:5 rows deleted from User Data Store",
                "INFO:authentication_service.tasks:Queued deletion confirmation for Username"
                f" ({self.user.id}) to Del Eter (deleter@example.com)",
            ])

        self.assertFalse(Token.objects.filter(user=self.user).exists())

        self.assertFalse(UserConsent.objects.filter(user=self.user).exists())

        self.assertFalse(Code.objects.filter(user=self.user).exists())

        self.assertFalse(UserSite.objects.filter(user=self.user).exists())

        self.assertFalse(UserSecurityQuestion.objects.filter(user=self.user).exists())

        with self.assertRaises(models.UserSite.DoesNotExist):
            models.UserSite.objects.get(id=self.user_site.id)

        user_model = get_user_model()
        with self.assertRaises(user_model.DoesNotExist):
            user_model.objects.get(id=self.user.id)

    def test_delete_user_and_data_task_nonexistent_user(self):
        user_id = uuid.uuid4()
        with self.assertLogs(level=logging.DEBUG) as logger:
            tasks.delete_user_and_data_task(
                user_id=user_id,
                deleter_id=self.deleter.id,
                reason="Because this is a test"
            )

        self.assertEquals(
            logger.output, [
                f"ERROR:authentication_service.tasks:User {user_id} cannot be deleted "
                "because it does not exist."
            ])
