# NOTE: Management command only to be used for setting up demo environments, do
# not use for anything else. Clients being set is bad enough, however the super
# user is created with an unsecure password that is visible in clear text in a
# public repo.
import datetime
import os
from base64 import b32encode

import sys

from django.conf import settings
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
        c, created = Client.objects.update_or_create(
            client_id="client_id_1",
            defaults={
                "name": "Wagtail client 1",
                "client_secret": "super_client_secret_1",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("WAGTAIL_1_CALLBACK", 'http://example.com/')
                ],
                "post_logout_redirect_uris": [
                    os.environ.get("WAGTAIL_1_LOGOUT_REDIRECT", 'http://example.com/')
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        self.stdout.write(self.style.SUCCESS(f"Creating site for {c}..."))
        site = settings.ACCESS_CONTROL_API.site_create(data={
            "domain_id": 1,
            "name": "springster",
            "client_id": c.id
        })
        self.stdout.write(self.style.SUCCESS(f"Created site for {c}..."))

        self.stdout.write(self.style.SUCCESS(f"Creating schema for {site}..."))
        schema = settings.USER_DATA_STORE_API.sitedataschema_create(data={
            "site_id": site.id,
            "schema": {"type": "data"}
        })
        self.stdout.write(self.style.SUCCESS(f"Created schema for {site}..."))

        c, created = Client.objects.update_or_create(
            client_id="client_id_2",
            defaults={
                "name": "Wagtail client 2",
                "client_secret": "super_client_secret_2",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("WAGTAIL_2_CALLBACK", 'http://example.com/')
                ],
                "post_logout_redirect_uris": [
                    os.environ.get("WAGTAIL_2_LOGOUT_REDIRECT", 'http://example.com/')
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        self.stdout.write(self.style.SUCCESS(f"Creating site for {c}..."))
        site = settings.ACCESS_CONTROL_API.site_create(data={
            "domain_id": 1,
            "name": "ninyampinga",
            "client_id": c.id
        })
        self.stdout.write(self.style.SUCCESS(f"Created site for {c}..."))

        self.stdout.write(self.style.SUCCESS(f"Creating schema for {site}..."))
        schema = settings.USER_DATA_STORE_API.sitedataschema_create(data={
            "site_id": site.id,
            "schema": {"type": "data"}
        })
        self.stdout.write(self.style.SUCCESS(f"Created schema for {site}..."))

        c, created = Client.objects.update_or_create(
            client_id="management_layer_workaround",
            defaults={
                "name": "Management Layer UI Temporary Workaround",
                "client_secret": "management_layer_workaround",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("MANAGEMENT_LAYER_WORKAROUND_REDIRECT",
                                   "http://localhost:8000/ui/oauth2-redirect.html"),
                    "http://core-management-layer:8000/ui/oauth2-redirect.html"
                ],
                "post_logout_redirect_uris": [],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        self.stdout.write(self.style.SUCCESS(f"Creating site for {c}..."))
        site = settings.ACCESS_CONTROL_API.site_create(data={
            "domain_id": 1,
            "name": "management_layer_workaround",
            "client_id": c.id
        })
        self.stdout.write(self.style.SUCCESS(f"Created site for {c}..."))

        self.stdout.write(self.style.SUCCESS(f"Creating schema for {site}..."))
        schema = settings.USER_DATA_STORE_API.sitedataschema_create(data={
            "site_id": site.id,
            "schema": {"type": "data"}
        })
        self.stdout.write(self.style.SUCCESS(f"Created schema for {site}..."))

        c, created = Client.objects.update_or_create(
            client_id="springster_integration",
            defaults={
                "name": "Springster Integration",
                "client_secret": "springster_integration",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    "http://localhost:8000/oidc/callback/",
                ],
                "post_logout_redirect_uris": [],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        self.stdout.write(self.style.SUCCESS(f"Creating site for {c}..."))
        site = settings.ACCESS_CONTROL_API.site_create(data={
            "domain_id": 1,
            "name": "springster_integration",
            "client_id": c.id
        })
        self.stdout.write(self.style.SUCCESS(f"Created site for {c}..."))

        self.stdout.write(self.style.SUCCESS(f"Creating schema for {site}..."))
        schema = settings.USER_DATA_STORE_API.sitedataschema_create(data={
            "site_id": site.id,
            "schema": {"type": "data"}
        })
        self.stdout.write(self.style.SUCCESS(f"Created schema for {site}..."))

        c, created = Client.objects.update_or_create(
            client_id="management_portal",
            defaults={
                "name": "Management Portal",
                "client_type": "public",
                "response_type": "id_token token",
                "jwt_alg": "RS256",
                "redirect_uris": [
                    "http://localhost:3000/oidc/callback/",
                    "http://core-management-portal:3000/#/oidc/callback?"
                ],
                "post_logout_redirect_uris": [
                    "http://localhost:3000/oidc/callback/",
                    "http://core-management-portal:3000/"
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        self.stdout.write(self.style.SUCCESS(f"Creating site for {c}..."))
        site = settings.ACCESS_CONTROL_API.site_create(data={
            "domain_id": 1,
            "name": "management_portal",
            "client_id": c.id
        })
        self.stdout.write(self.style.SUCCESS(f"Created site for {c}..."))

        self.stdout.write(self.style.SUCCESS(f"Creating schema for {site}..."))
        schema = settings.USER_DATA_STORE_API.sitedataschema_create(data={
            "site_id": site.id,
            "schema": {"type": "data"}
        })
        self.stdout.write(self.style.SUCCESS(f"Created schema for {site}..."))

        # Super user
        self.stdout.write(self.style.SUCCESS("Creating superuser..."))
        user, created = get_user_model().objects.update_or_create(
            username="admin",
            defaults={
                "is_superuser": 1,
                "is_staff": 1,
                "birth_date": datetime.date(2000, 1, 1)
            }
        )
        user.set_password("local")
        user.save()
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", user.username
        )))

        # End User
        end_user, created = get_user_model().objects.update_or_create(
            username="enduser",
            defaults={
                "first_name": "End",
                "last_name": "User",
                "email": "enduser@here.com",
                "nickname": "l33t",
                "birth_date": datetime.date(2000, 1, 1)
            }
        )
        end_user.set_password("enduser")
        end_user.save()
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", end_user.username
        )))

        # System User
        system_user, created = get_user_model().objects.update_or_create(
            username="sysuser",
            defaults={
                "first_name": "System",
                "last_name": "User",
                "email": "sysuser@here.com",
                "nickname": "5y5",
                "birth_date": datetime.date(2000, 1, 1)
            }
        )
        system_user.set_password("sysuser")
        system_user.save()
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", system_user.username
        )))

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
        sys.stdout.write(self.style.SUCCESS(
            "Created system user with OTP URL: {}".format(get_otpauth_url(
                accountname=system_user.username,
                secret=b32encode(totp_device.bin_key),
                issuer="Girl Effect Demo",
                digits=totp_device.digits)
        )))

        call_command("load_security_questions")
