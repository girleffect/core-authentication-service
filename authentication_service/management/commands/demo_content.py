# NOTE: Management command only to be used for setting up demo environments, do
# not use for anything else. Clients being set is bad enough, however the super
# user is created with an unsecure password that is visible in clear text in a
# public repo.
import datetime
import os
from base64 import b32encode

import sys
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice

from oidc_provider.models import Client
from two_factor.utils import get_otpauth_url


class Command(BaseCommand):
    help = "Setup used for demonstration purposes only"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating clients..."))
        c = Client(
            name="Wagtail client 1",
            client_id="client_id_1",
            client_secret="super_client_secret_1",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=[
                os.environ.get("WAGTAIL_1_IP",'http://example.com/')
            ]
        )
        c.save()

        c = Client(
            name="Wagtail client 2",
            client_id="client_id_2",
            client_secret="super_client_secret_2",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=[
                os.environ.get("WAGTAIL_2_IP",'http://example.com/')
            ]
        )
        c.save()

        # Super user
        self.stdout.write(self.style.SUCCESS("Creating superuser..."))
        user = get_user_model().objects.create(username="admin", is_superuser=1, is_staff=1,
                                               birth_date=datetime.date(2000, 1, 1))
        user.set_password("local")
        user.save()

        # End User
        end_user = get_user_model().objects.create(
            username="enduser", first_name="End", last_name="User",
            email="enduser@here.com", nickname="l33t",
            birth_date=datetime.date(2000, 1, 1)
        )
        end_user.set_password("enduser")
        end_user.save()

        # System User
        system_user = get_user_model().objects.create(
            username="sysuser", first_name="System", last_name="User",
            email="sysuser@here.com", nickname="5y5",
            birth_date=datetime.date(2000, 1, 1)
        )
        system_user.set_password("sysuser")
        system_user.save()

        # System User 2FA Device. We set up a device that will always generate
        # the following URL that can be used to create a QR code:
        # otpauth://totp/Girl%2520Effect%2520Demo%3A%20sysuser?secret=VFFGMP7P36Q7TIZV3YZ65ZLHKQPAPXIM&digits=6&issuer=Girl%2520Effect%2520Demo
        totp_device, created = TOTPDevice.objects.update_or_create(
            key="a94a663fefdfa1f9a335de33eee567541e07dd0c",
            user=system_user,
            name="default",
            confirmed=True
        )
        totp_device.save()
        sys.stdout.write(get_otpauth_url(
            accountname=system_user.username,
            secret=b32encode(totp_device.bin_key),
            issuer="Girl Effect Demo",
            digits=totp_device.digits
        ))

        call_command("load_security_questions")
