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
from django_otp.plugins.otp_totp.models import TOTPDevice

from oidc_provider.models import Client
from two_factor.utils import get_otpauth_url

from user_data_store.rest import ApiException


class Command(BaseCommand):
    help = "Setup used for demonstration purposes only"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-api-calls",
            action="store_true",
            help="Don't create objects that make api calls.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating clients..."))
        c, created = Client.objects.update_or_create(
            client_id="client_id_1",
            defaults={
                "name": "Wagtail Demo 1 Site 1",
                "client_secret": "super_client_secret_1",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("WAGTAIL_1_CALLBACK", 'http://example.com/'),
                    os.environ.get(
                        "WAGTAIL_1_LOGOUT_REDIRECT",
                        'http://example.com/') + "register-redirect/",
                    os.environ.get("WAGTAIL_1_LOGOUT_REDIRECT", 'http://example.com/')
                ],
                "post_logout_redirect_uris": [
                    os.environ.get("WAGTAIL_1_LOGOUT_REDIRECT", 'http://example.com/')
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        c, created = Client.objects.update_or_create(
            client_id="client_id_2",
            defaults={
                "name": "Wagtail Demo 2 Site 1",
                "client_secret": "super_client_secret_2",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("WAGTAIL_2_CALLBACK", 'http://example.com/'),
                    os.environ.get(
                        "WAGTAIL_2_LOGOUT_REDIRECT",
                        'http://example.com/') + "register-redirect/",
                    os.environ.get("WAGTAIL_2_LOGOUT_REDIRECT", 'http://example.com/')
                ],
                "post_logout_redirect_uris": [
                    os.environ.get("WAGTAIL_2_LOGOUT_REDIRECT", 'http://example.com/')
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        c, created = Client.objects.update_or_create(
            client_id="client_id_3",
            defaults={
                "name": "Wagtail Demo 1 Site 2",
                "client_secret": "super_client_secret_3",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    os.environ.get("WAGTAIL_3_CALLBACK", 'http://example.com/'),
                    os.environ.get(
                        "WAGTAIL_3_LOGOUT_REDIRECT",
                        'http://example.com/') + "register-redirect/",
                    os.environ.get("WAGTAIL_3_LOGOUT_REDIRECT", 'http://example.com/')
                    ],
                "post_logout_redirect_uris": [
                    os.environ.get("WAGTAIL_3_LOGOUT_REDIRECT", 'http://example.com/')
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        c, created = Client.objects.update_or_create(
            client_id="management_layer_workaround",
            defaults={
                "name": "Management Layer Workaround",
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

        c, created = Client.objects.update_or_create(
            client_id="corporate_site",
            defaults={
                "name": "Corporate Site",
                "client_secret": "corporate_site_secret",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    "http://core-corporate-site/oidc/callback/",
                ],
                "post_logout_redirect_uris": [
                    "http://core-corporate-site/",
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        c, created = Client.objects.update_or_create(
            client_id="management_portal",
            defaults={
                "name": "Management Portal",
                "client_type": "public",
                "response_type": "id_token token",
                "jwt_alg": "RS256",
                "redirect_uris": [
                    "http://localhost:3000/oidc/callback/",
                    "http://core-management-portal/#/oidc/callback?"
                ],
                "post_logout_redirect_uris": [
                    "http://localhost:3000/oidc/callback/",
                    "http://core-management-portal/"
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        c, created = Client.objects.update_or_create(
            client_id="core_data_ingestion",
            defaults={
                "name": "Data ingestion service",
                "client_secret": "core_data_ingestion_secret",
                "response_type": "code",
                "jwt_alg": "HS256",
                "redirect_uris": [
                    "http://core-data-ingestion-site:8000/oidc/callback/",
                ],
                "post_logout_redirect_uris": [
                    "http://core-data-ingestion-site/",
                ],
            }
        )
        self.stdout.write(self.style.SUCCESS("{} {}".format(
            "Created" if created else "Updated", c.client_id
        )))

        # Set up Site and SiteDataSchema objects
        if not options["no_api_calls"]:
            for client in Client.objects.all():
                sites = settings.ACCESS_CONTROL_API.site_list(client_id=client.id)
                if sites:
                    self.stdout.write(
                        self.style.SUCCESS(f"Updating site for {client.name}..."))
                    site = settings.ACCESS_CONTROL_API.site_update(sites[0].id, data={
                        "domain_id": 1,
                        "name": client.name,
                        "client_id": client.id
                    })
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated site for {client.name}..."))
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"Creating site for {client.name}..."))
                    site = settings.ACCESS_CONTROL_API.site_create(data={
                        "domain_id": 1,
                        "name": client.name,
                        "client_id": client.id,
                        "description": ""
                    })
                    self.stdout.write(
                        self.style.SUCCESS(f"Created site for {client.name}..."))

                try:
                    schema = settings.USER_DATA_STORE_API.sitedataschema_read(site.id)
                    self.stdout.write(
                        self.style.SUCCESS(f"Updating schema for {site.name}..."))
                    schema = settings.USER_DATA_STORE_API.sitedataschema_update(schema.site_id,
                                                                                data={
                                                                                    "schema": {"type": "object"}
                                                                                })
                    self.stdout.write(
                        self.style.SUCCESS(f"Updating schema for {site.name}..."))
                except ApiException as e:
                    if e.status == 404:
                        self.stdout.write(
                            self.style.SUCCESS(f"Creating schema for {site.name}..."))
                        schema = settings.USER_DATA_STORE_API.sitedataschema_create(
                        data={
                            "site_id": site.id,
                            "schema": {"type": "object"}
                        })
                        self.stdout.write(
                            self.style.SUCCESS(f"Created schema for {site.name}..."))
                    else:
                        raise

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
        call_command("load_countries")
        call_command("load_organisations")
