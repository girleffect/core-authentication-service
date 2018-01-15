from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice


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

        cls.static_device = TOTPDevice.objects.create(
            user=cls.twofa_user,
            name="default",
            confirmed=True
        )

    def get_credential_step(self):
        print("Getting credential step")
        response = self.client.get(
            self.wizard_url,
            follow=True
        )
        return response

    def post_credential_step(self):
        print("Posting credential step")
        response = self.client.post(
            self.wizard_url,
            {
                "login_view-current_step": "credentials",
                "credentials-username": "standard_user",
                "credentials-password": "1234"
            },
            follow=True
        )
        return response


class StandardTestCase(BaseTestCase):
    """Test case for users without 2FA enabled"""
    def test_it(self):
        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step. We check for a username field in the response
        # since only staff memebers will actually have access to admin, other
        # users will see another login screen.
        response = self.post_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")


class TwoFATestCase(BaseTestCase):
    """Test case for users with 2FA enabled"""
    def test_id(self):
        # Get credentials step
        response = self.get_credential_step()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")

        # Post credentials step
        response = self.post_credential_step()
        self.assertEqual(response.status_code, 200)
        import pdb; pdb.set_trace()
        self.assertContains(response, "Token")


