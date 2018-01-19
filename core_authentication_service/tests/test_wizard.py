from django.test import TestCase
from django.urls import reverse
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from core_authentication_service.models import CoreUser as User


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(BaseTestCase, cls).setUpTestData()
        cls.wizard_url = reverse("login")

        cls.standard_user = User.objects.create(
            username="standard_user"
        )
        cls.standard_user.set_password("1234")
        cls.standard_user.save()

        cls.twofa_user = User.objects.create(
            username="2fa_user"
        )
        cls.twofa_user.set_password("1234")
        cls.twofa_user.save()

        cls.totp_device = TOTPDevice.objects.create(
            user=cls.twofa_user,
            name="default",
            confirmed=True,
            key=random_hex().decode()
        )

        cls.super_user = User.objects.create_superuser(
            username="super_user", email="super@user.com",
            password="1234"
        )
        cls.super_user.save()

    def get_credential_step(self):
        print("Getting credential step")
        response = self.client.get(
            self.wizard_url,
            follow=True
        )
        return response

    def post_credential_step(self, user, password):
        print("Posting credential step")
        response = self.client.post(
            self.wizard_url,
            {
                "login_view-current_step": "auth",
                "auth-username": user,
                "auth-password": password
            },
            follow=True
        )
        return response

    def post_token_step(self):
        print("Posting token step")
        response = self.client.post(
            self.wizard_url,
            {
                "login_view-current_step": "token",
                "token-otp_token": totp(self.totp_device.bin_key)
            },
            follow=True
        )
        return response

    def post_backup_step(self, token):
        print("Posting backup step")
        response = self.client.post(
            self.wizard_url,
            {
                "login_view-current_step": "backup",
                "backup-otp_token": token
            },
            follow=True
        )
        return response


class StandardTestCase(BaseTestCase):
    """Test case for users without 2FA enabled."""
    def test_it(self):
        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step. We check for a username field in the response
        # since only staff memebers will actually have access to admin, other
        # users will see another login screen.
        response = self.post_credential_step(self.standard_user, "1234")
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/login/?next=/admin/")


class TwoFATestCase(BaseTestCase):
    """Test case for users with 2FA enabled."""
    def test_it(self):
        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step
        response = self.post_credential_step(self.twofa_user, "1234")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Token")

        # Post token step
        response = self.post_token_step()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/login/?next=/admin/")


class BackupCodeTestCase(BaseTestCase):
    """Test case where user uses one of their backup codes."""
    def test_it(self):
        # Create backup tokens for user
        device = self.twofa_user.staticdevice_set.create(name='backup')
        device.token_set.create(token='abcdef123')

        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step
        response = self.post_credential_step(self.twofa_user, "1234")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "backup token")

        # Should be able to go to backup tokens step in wizard
        response = self.client.post(
            self.wizard_url, {"wizard_goto_step": "backup"}, follow=True
        )
        self.assertContains(response, "Token")

        # Don't accept invalid tokens
        response = self.client.post(
            self.wizard_url,
            {
                "backup-otp_token": "WRONG",
                "login_view-current_step": "backup"
            },
            follow=True
        )
        self.assertEqual(
            response.context_data["wizard"]["form"].errors,
            {"__all__":
                ["Invalid token. Please make sure you have entered it "
                 "correctly."]
             }
        )

        # Post backup step
        response = self.post_backup_step("abcdef123")
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/login/?next=/admin/")


class SuperUserTestCase(BaseTestCase):
    """Test case for superusers. These users will/should be signed in"""
    def test_it(self):
        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step. Since 2FA isn't set up on the superuser
        # account, they should immediately be signed into the admin interface.
        response = self.post_credential_step(self.super_user, "1234")
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, "/admin/")
