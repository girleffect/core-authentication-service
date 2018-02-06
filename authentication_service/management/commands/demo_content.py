# NOTE: Management command only to be used for setting up demo environments, do
# not use for anything else. Clients being set is bad enough, however the super
# user is created with an unsecure password that is visible in clear text in a
# public repo.

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management import call_command

from oidc_provider.models import Client


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
        user = get_user_model().objects.create(username="admin", is_superuser=1, is_staff=1)
        user.set_password("local")
        user.save()

        call_command("load_security_questions")
